// The bundled Python engine (#124): started as a Tauri sidecar on launch and
// stopped on quit. The window still talks to it over the loopback API; this
// module only owns the process and reports why the engine is not up.

use std::io::{Read, Write};
use std::net::{Ipv4Addr, SocketAddr, TcpListener, TcpStream};
use std::sync::{Condvar, Mutex};
use std::time::Duration;

use serde::Serialize;
use tauri::{AppHandle, Manager};
use tauri_plugin_shell::process::{CommandChild, CommandEvent};
use tauri_plugin_shell::ShellExt;

pub const ENGINE_PORT: u16 = 47811;
const SIDECAR: &str = "tmodel-engine";
const STDERR_LINES: usize = 5;

/// What the app knows about the engine process, for the window to explain.
#[derive(Clone, Debug, PartialEq, Serialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum EngineProcess {
    /// Our sidecar was started; it may still be starting up.
    Started,
    /// A tmodel engine was already answering on the port (e.g. `tmodel serve`).
    External,
    /// Something that is not a tmodel engine holds the port.
    PortBusy { port: u16 },
    /// The sidecar could not be started at all.
    SpawnFailed { error: String },
    /// The sidecar exited; `stderr` holds its last lines.
    Exited { code: Option<i32>, stderr: String },
}

#[derive(Default)]
pub struct EngineState {
    process: Mutex<Option<EngineProcess>>,
    child: Mutex<Option<CommandChild>>,
    stderr: Mutex<Vec<String>>,
    exited: Condvar,
}

impl EngineState {
    fn set(&self, p: EngineProcess) {
        *self.process.lock().unwrap() = Some(p);
        self.exited.notify_all();
    }
}

fn loopback(port: u16) -> SocketAddr {
    SocketAddr::from((Ipv4Addr::LOCALHOST, port))
}

/// Is the port free to bind on loopback?
pub fn port_is_free(port: u16) -> bool {
    TcpListener::bind(loopback(port)).is_ok()
}

/// Does a tmodel engine answer `/health` on the port?
pub fn tmodel_engine_answers(port: u16) -> bool {
    let Ok(mut stream) = TcpStream::connect_timeout(&loopback(port), Duration::from_millis(500))
    else {
        return false;
    };
    let _ = stream.set_read_timeout(Some(Duration::from_millis(1000)));
    let request = "GET /health HTTP/1.0\r\nHost: 127.0.0.1\r\n\r\n";
    if stream.write_all(request.as_bytes()).is_err() {
        return false;
    }
    let mut body = String::new();
    let _ = stream.take(64 * 1024).read_to_string(&mut body);
    body.contains("\"tmodel-engine\"")
}

/// Decide what to do about the port, then start the sidecar if it is ours to start.
pub fn start(app: &AppHandle) {
    let state = app.state::<EngineState>();
    if !port_is_free(ENGINE_PORT) {
        state.set(if tmodel_engine_answers(ENGINE_PORT) {
            EngineProcess::External
        } else {
            EngineProcess::PortBusy { port: ENGINE_PORT }
        });
        return;
    }

    // The one-file engine runs as a launcher plus the Python process. A process
    // group permits killing both if needed. --exit-with-parent stops the engine
    // when stdin closes, on normal quit as well as app crash or forced quit.
    let spawned = app.shell().sidecar(SIDECAR).and_then(|cmd| {
        cmd.args([
            "serve",
            "--port",
            &ENGINE_PORT.to_string(),
            "--exit-with-parent",
        ])
        .set_process_group(true)
        .spawn()
    });
    let (mut rx, child) = match spawned {
        Ok(pair) => pair,
        Err(err) => {
            state.set(EngineProcess::SpawnFailed {
                error: err.to_string(),
            });
            return;
        }
    };
    *state.child.lock().unwrap() = Some(child);
    state.set(EngineProcess::Started);

    let app = app.clone();
    tauri::async_runtime::spawn(async move {
        while let Some(event) = rx.recv().await {
            let state = app.state::<EngineState>();
            match event {
                CommandEvent::Stderr(line) => {
                    let mut lines = state.stderr.lock().unwrap();
                    lines.push(String::from_utf8_lossy(&line).trim_end().to_string());
                    let excess = lines.len().saturating_sub(STDERR_LINES);
                    lines.drain(..excess);
                }
                CommandEvent::Terminated(payload) => {
                    state.child.lock().unwrap().take();
                    let stderr = state.stderr.lock().unwrap().join("\n");
                    state.set(EngineProcess::Exited {
                        code: payload.code,
                        stderr,
                    });
                }
                _ => {}
            }
        }
    });
}

/// Close stdin so the engine exits normally and PyInstaller removes its unpacked
/// runtime. SIGKILL would stop both processes but leave an _MEI directory behind.
pub fn stop(app: &AppHandle) {
    let state = app.state::<EngineState>();
    let child = state.child.lock().unwrap().take();
    if let Some(child) = child {
        drop(child);
        // Let the event reader observe termination before the app exits. This
        // also avoids immediately reopening against the old engine. Bound the
        // wait so a broken sidecar cannot hang the desktop app indefinitely.
        let process = state.process.lock().unwrap();
        let _ = state
            .exited
            .wait_timeout_while(process, Duration::from_secs(10), |p| {
                matches!(p, Some(EngineProcess::Started))
            });
    }
}

/// For the window: what happened to the engine process, if anything.
#[tauri::command]
pub fn engine_process(state: tauri::State<'_, EngineState>) -> Option<EngineProcess> {
    state.process.lock().unwrap().clone()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn busy_port_is_detected() {
        let listener = TcpListener::bind(loopback(0)).unwrap();
        let port = listener.local_addr().unwrap().port();
        assert!(!port_is_free(port));
        drop(listener);
        assert!(port_is_free(port));
    }

    #[test]
    fn a_port_with_no_engine_is_not_tmodel() {
        let listener = TcpListener::bind(loopback(0)).unwrap();
        let port = listener.local_addr().unwrap().port();
        std::thread::spawn(move || {
            if let Ok((mut s, _)) = listener.accept() {
                let mut buf = [0u8; 512];
                let _ = s.read(&mut buf);
                let _ = s.write_all(b"HTTP/1.0 200 OK\r\n\r\n{\"service\": \"something-else\"}");
            }
        });
        assert!(!tmodel_engine_answers(port));
    }

    #[test]
    fn a_tmodel_engine_is_recognised() {
        let listener = TcpListener::bind(loopback(0)).unwrap();
        let port = listener.local_addr().unwrap().port();
        std::thread::spawn(move || {
            if let Ok((mut s, _)) = listener.accept() {
                let mut buf = [0u8; 512];
                let _ = s.read(&mut buf);
                let _ = s.write_all(
                    b"HTTP/1.0 200 OK\r\n\r\n{\"status\": \"ok\", \"engine\": \"tmodel-engine\"}",
                );
            }
        });
        assert!(tmodel_engine_answers(port));
    }

    #[test]
    fn process_states_serialise_for_the_window() {
        let json = serde_json::to_string(&EngineProcess::PortBusy { port: 47811 }).unwrap();
        assert_eq!(json, r#"{"kind":"port_busy","port":47811}"#);
        let json = serde_json::to_string(&EngineProcess::Exited {
            code: Some(1),
            stderr: "boom".into(),
        })
        .unwrap();
        assert_eq!(json, r#"{"kind":"exited","code":1,"stderr":"boom"}"#);
    }
}

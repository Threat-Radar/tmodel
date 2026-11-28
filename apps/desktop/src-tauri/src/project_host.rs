//! Native grants for #288 projects and #289 review sessions (#290's host contract).

use std::fs::{self, OpenOptions};
use std::io::{Read, Write};
use std::net::{Ipv4Addr, SocketAddr, TcpStream};
use std::os::unix::fs::{MetadataExt, OpenOptionsExt};
use std::path::{Path, PathBuf};
use std::sync::Mutex;
use std::time::{Duration, Instant};

use hmac::{Hmac, Mac};
use serde::Deserialize;
use serde_json::{json, Value};
use sha2::Sha256;
use tauri::{AppHandle, Manager, WebviewWindow};
use tauri_plugin_dialog::{DialogExt, FilePath};

use crate::engine::{EngineState, ENGINE_PORT};

const PROOF_DOMAIN: &[u8] = b"tmodel-host-session-v1:";
const MAX_RESPONSE: u64 = 32 * 1024 * 1024;
const MAX_MODEL_TEXT: usize = 16 * 1024 * 1024;

// Intentionally neither Debug nor Serialize: credentials must not enter logs.
#[derive(Clone)]
pub struct HostCredentials {
    pub token: String,
    pub identity: String,
}

#[derive(Default)]
pub struct ProjectHostState(Mutex<Option<HostCredentials>>);

impl ProjectHostState {
    pub fn initialize(&self, directory: &Path) -> Result<HostCredentials, String> {
        let credentials = HostCredentials {
            token: random_hex(32)?,
            identity: reviewer_identity(directory)?,
        };
        *self
            .0
            .lock()
            .map_err(|_| "Project session is unavailable.")? = Some(credentials.clone());
        Ok(credentials)
    }

    pub fn clear(&self) {
        if let Ok(mut value) = self.0.lock() {
            *value = None;
        }
    }

    fn credentials(&self) -> Result<HostCredentials, String> {
        self.0
            .lock()
            .map_err(|_| "Project session is unavailable.")?
            .clone()
            .ok_or_else(|| "This engine has no desktop project session.".into())
    }
}

fn random_hex(bytes: usize) -> Result<String, String> {
    let mut value = vec![0; bytes];
    getrandom::fill(&mut value).map_err(|_| "Cannot initialize a private project session.")?;
    Ok(value.iter().map(|byte| format!("{byte:02x}")).collect())
}

fn reviewer_identity(directory: &Path) -> Result<String, String> {
    fs::create_dir_all(directory).map_err(|_| "Cannot open the desktop identity directory.")?;
    let path = directory.join("reviewer-id");
    let generated = random_hex(16)?;
    match OpenOptions::new()
        .write(true)
        .create_new(true)
        .mode(0o600)
        .open(&path)
    {
        Ok(mut file) => {
            file.write_all(generated.as_bytes())
                .and_then(|()| file.sync_all())
                .map_err(|_| "Cannot save the desktop reviewer identity.")?;
        }
        Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => {}
        Err(_) => return Err("Cannot save the desktop reviewer identity.".into()),
    }
    let metadata = fs::symlink_metadata(&path).map_err(|_| "Cannot read the desktop identity.")?;
    // SAFETY: getuid has no preconditions; it returns this process's real OS uid.
    let uid = unsafe { libc::getuid() };
    if !metadata.is_file() || metadata.uid() != uid || metadata.mode() & 0o077 != 0 {
        return Err("The desktop identity must be a private file owned by this OS user.".into());
    }
    let mut identity = String::new();
    OpenOptions::new()
        .read(true)
        .custom_flags(libc::O_NOFOLLOW)
        .open(&path)
        .and_then(|file| file.take(65).read_to_string(&mut identity))
        .map_err(|_| "Cannot read the desktop identity.")?;
    if identity.len() != 32
        || !identity
            .bytes()
            .all(|byte| byte.is_ascii_digit() || (b'a'..=b'f').contains(&byte))
    {
        return Err("The saved desktop identity is invalid.".into());
    }
    Ok(format!("party:local:{identity}:{uid}"))
}

fn raw_request(
    port: u16,
    method: &str,
    route: &str,
    token: Option<&str>,
    body: &Value,
) -> Result<(u16, Value), String> {
    let address = SocketAddr::from((Ipv4Addr::LOCALHOST, port));
    let mut socket = TcpStream::connect_timeout(&address, Duration::from_millis(500))
        .map_err(|_| "The desktop engine is not available.")?;
    socket
        .set_read_timeout(Some(Duration::from_secs(30)))
        .map_err(|_| "Cannot read from the engine.")?;
    socket
        .set_write_timeout(Some(Duration::from_secs(5)))
        .map_err(|_| "Cannot write to the engine.")?;
    let payload = if method == "POST" {
        serde_json::to_vec(body).map_err(|_| "Invalid project request.")?
    } else {
        Vec::new()
    };
    let authorization = token
        .map(|value| format!("Authorization: Bearer {value}\r\n"))
        .unwrap_or_default();
    let header = format!("{method} {route} HTTP/1.0\r\nHost: 127.0.0.1:{port}\r\n{authorization}Content-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n", payload.len());
    socket
        .write_all(header.as_bytes())
        .and_then(|()| socket.write_all(&payload))
        .map_err(|_| "The engine request failed.")?;
    let mut response = Vec::new();
    socket
        .take(MAX_RESPONSE + 1)
        .read_to_end(&mut response)
        .map_err(|_| "The engine response failed.")?;
    if response.len() as u64 > MAX_RESPONSE {
        return Err("The engine response is too large.".into());
    }
    let offset = response
        .windows(4)
        .position(|part| part == b"\r\n\r\n")
        .ok_or("The engine returned an invalid HTTP response.")?;
    let status = std::str::from_utf8(&response[..offset])
        .ok()
        .and_then(|headers| headers.lines().next())
        .and_then(|line| line.split_whitespace().nth(1))
        .and_then(|code| code.parse::<u16>().ok())
        .ok_or("The engine returned an invalid status.")?;
    let answer: Value = serde_json::from_slice(&response[offset + 4..])
        .map_err(|_| "The engine returned invalid JSON.")?;
    Ok((status, answer))
}

fn request(
    port: u16,
    method: &str,
    route: &str,
    token: Option<&str>,
    body: &Value,
) -> Result<Value, String> {
    let (status, answer) = raw_request(port, method, route, token, body)?;
    if !(200..300).contains(&status) {
        let message = answer
            .pointer("/error/message")
            .and_then(Value::as_str)
            .unwrap_or("The project operation failed.");
        if token.is_some_and(|secret| message.contains(secret)) {
            return Err("The project operation failed.".into());
        }
        return Err(message.chars().take(4096).collect());
    }
    Ok(answer)
}

fn verify_proof(key: &str, challenge: &str, answer: &Value) -> bool {
    if answer.get("challenge").and_then(Value::as_str) != Some(challenge) {
        return false;
    }
    let Some(proof) = answer.get("proof").and_then(Value::as_str) else {
        return false;
    };
    if proof.len() != 64
        || !proof
            .bytes()
            .all(|byte| byte.is_ascii_digit() || (b'a'..=b'f').contains(&byte))
    {
        return false;
    }
    let Ok(bytes) = (0..proof.len())
        .step_by(2)
        .map(|offset| u8::from_str_radix(&proof[offset..offset + 2], 16))
        .collect::<Result<Vec<_>, _>>()
    else {
        return false;
    };
    let Ok(mut mac) = Hmac::<Sha256>::new_from_slice(key.as_bytes()) else {
        return false;
    };
    mac.update(PROOF_DOMAIN);
    mac.update(challenge.as_bytes());
    mac.verify_slice(&bytes).is_ok()
}

fn verify_engine(port: u16, credentials: &HostCredentials) -> Result<bool, String> {
    let challenge = random_hex(32)?;
    let (status, answer) = raw_request(
        port,
        "GET",
        &format!("/host/health?challenge={challenge}"),
        None,
        &Value::Null,
    )?;
    if status == 503
        && answer.pointer("/error/code").and_then(Value::as_str) == Some("workspace_failure")
    {
        return Ok(false); // Read-only engine: do not delay the home screen.
    }
    if !(200..300).contains(&status) || !verify_proof(&credentials.token, &challenge, &answer) {
        return Err("The service on the engine port is not this desktop session's engine.".into());
    }
    Ok(true)
}

fn trusted_window(window: &WebviewWindow) -> Result<(), String> {
    let url = window
        .url()
        .map_err(|_| "Cannot verify the application window.")?;
    let production = (url.scheme() == "tauri" && url.host_str() == Some("localhost"))
        || (url.scheme() == "https" && url.host_str() == Some("tauri.localhost"));
    let development = cfg!(debug_assertions)
        && url.scheme() == "http"
        && url.port() == Some(1420)
        && matches!(url.host_str(), Some("localhost" | "127.0.0.1"));
    if window.label() != "main" || !(production || development) {
        return Err("Project access is restricted to the desktop application's own window.".into());
    }
    Ok(())
}

#[tauri::command]
pub async fn project_host_session(
    window: WebviewWindow,
    app: AppHandle,
) -> Result<Option<String>, String> {
    trusted_window(&window)?;
    if !app.state::<EngineState>().owned() {
        return Ok(None);
    }
    let Ok(credentials) = app.state::<ProjectHostState>().credentials() else {
        return Ok(None);
    };
    tauri::async_runtime::spawn_blocking(move || {
        let deadline = Instant::now() + Duration::from_secs(60);
        while app.state::<EngineState>().owned() && Instant::now() < deadline {
            match verify_engine(ENGINE_PORT, &credentials) {
                Ok(true) => return Ok(Some(credentials.token)),
                Ok(false) => return Ok(None),
                Err(_) => {} // Engine startup may still be in progress.
            }
            std::thread::sleep(Duration::from_millis(150));
        }
        Ok(None)
    })
    .await
    .map_err(|_| "The project session could not be verified.".to_string())?
}

#[derive(Deserialize)]
#[serde(tag = "kind", rename_all = "kebab-case", deny_unknown_fields)]
pub enum HostProjectStep {
    OpenProject {},
    OpenFile {},
    CreateProject { from: ProjectStart },
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ProjectStart {
    source_file: Option<String>,
    model_id: Option<String>,
    model_text: Option<String>,
    name: Option<String>,
}

fn native_path(path: Option<FilePath>) -> Result<Option<PathBuf>, String> {
    path.map(|value| {
        value
            .into_path()
            .map_err(|_| "Select a local folder or YAML file.".to_string())
    })
    .transpose()
}

fn valid_model_id(value: &str) -> bool {
    value
        .strip_prefix("project:")
        .or_else(|| value.strip_prefix("file:"))
        .is_some_and(|id| {
            id.len() == 32
                && id
                    .bytes()
                    .all(|byte| byte.is_ascii_digit() || (b'a'..=b'f').contains(&byte))
        })
}

fn project_call(credentials: &HostCredentials, route: &str, body: Value) -> Result<String, String> {
    if !verify_engine(ENGINE_PORT, credentials)? {
        return Err("Project folders are not enabled in this engine.".into());
    }
    let response = request(ENGINE_PORT, "POST", route, Some(&credentials.token), &body)?;
    response
        .get("model_id")
        .and_then(Value::as_str)
        .filter(|id| valid_model_id(id))
        .map(str::to_owned)
        .ok_or_else(|| "The engine returned no project or file id.".into())
}

#[tauri::command]
pub async fn project_host_step(
    window: WebviewWindow,
    app: AppHandle,
    step: HostProjectStep,
) -> Result<Option<String>, String> {
    trusted_window(&window)?;
    if !app.state::<EngineState>().owned() {
        return Err("This engine has no desktop project session.".into());
    }
    let credentials = app.state::<ProjectHostState>().credentials()?;
    tauri::async_runtime::spawn_blocking(move || {
        // Verify before showing any path grants, and again immediately before
        // each privileged request. An external health string grants nothing.
        if !verify_engine(ENGINE_PORT, &credentials)? {
            return Err("Project folders are not enabled in this engine.".into());
        }
        let (route, body) = match step {
            HostProjectStep::OpenProject {} => {
                let Some(path) = native_path(
                    app.dialog()
                        .file()
                        .set_title("Open project folder")
                        .blocking_pick_folder(),
                )?
                else {
                    return Ok(None);
                };
                ("/workspace/host/open-project", json!({"path":path}))
            }
            HostProjectStep::OpenFile {} => {
                let Some(path) = native_path(
                    app.dialog()
                        .file()
                        .set_title("Open threat model")
                        .add_filter("YAML model", &["yaml", "yml"])
                        .blocking_pick_file(),
                )?
                else {
                    return Ok(None);
                };
                ("/workspace/host/open-file", json!({"path":path}))
            }
            HostProjectStep::CreateProject { from } => {
                if usize::from(from.source_file.is_some())
                    + usize::from(from.model_id.is_some())
                    + usize::from(from.model_text.is_some())
                    != 1
                {
                    return Err("Choose one project source.".into());
                }
                let Some(path) = native_path(
                    app.dialog()
                        .file()
                        .set_title("Choose a new project folder")
                        .blocking_pick_folder(),
                )?
                else {
                    return Ok(None);
                };
                let mut body = json!({"path":path});
                if let Some(file) = from.source_file {
                    if Path::new(&file)
                        .file_name()
                        .and_then(|value| value.to_str())
                        != Some(&file)
                        || file.contains(['/', '\\'])
                    {
                        return Err("Choose an approved example by filename.".into());
                    }
                    body["source_file"] = json!(file);
                } else if let Some(model_id) = from.model_id {
                    if !valid_model_id(&model_id) {
                        return Err("Choose an opened model.".into());
                    }
                    body["model_id"] = json!(model_id);
                } else if let Some(text) = from.model_text {
                    if text.trim().is_empty() || text.len() > MAX_MODEL_TEXT {
                        return Err("The imported model is empty or too large.".into());
                    }
                    let Some(file) = native_path(
                        app.dialog()
                            .file()
                            .set_title("Save imported model YAML")
                            .set_file_name("imported-model.yaml")
                            .add_filter("YAML model", &["yaml", "yml"])
                            .blocking_save_file(),
                    )?
                    else {
                        return Ok(None);
                    };
                    // Never overwrite an existing source or follow a symlink.
                    let mut output = OpenOptions::new()
                        .write(true)
                        .create_new(true)
                        .mode(0o600)
                        .open(&file)
                        .map_err(|_| "Choose a new YAML filename; existing files are preserved.")?;
                    output
                        .write_all(text.as_bytes())
                        .and_then(|()| output.sync_all())
                        .map_err(|_| "The imported model could not be saved.")?;
                    body["model_id"] = json!(project_call(
                        &credentials,
                        "/workspace/host/open-file",
                        json!({"path":file})
                    )?);
                }
                if let Some(name) = from.name {
                    body["name"] = json!(name);
                }
                ("/workspace/host/create-project", body)
            }
        };
        project_call(&credentials, route, body).map(Some)
    })
    .await
    .map_err(|_| "The project operation did not finish.".to_string())?
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn proof_requires_the_session_key_and_current_challenge() {
        let key = "test-only-host-key-not-a-production-credential";
        let challenge = "a".repeat(64);
        let mut mac = Hmac::<Sha256>::new_from_slice(key.as_bytes()).unwrap();
        mac.update(PROOF_DOMAIN);
        mac.update(challenge.as_bytes());
        let proof: String = mac
            .finalize()
            .into_bytes()
            .iter()
            .map(|byte| format!("{byte:02x}"))
            .collect();
        let answer = json!({"challenge":challenge,"proof":proof});
        // Shared with Python's test_host_reviews.py; catches a wire mismatch.
        assert_eq!(
            answer["proof"],
            "a5098e6f9bfc3cd5b4fe96e5c06c812417af83a49fa8284384be1cda95fa7acc"
        );
        assert!(verify_proof(key, &challenge, &answer));
        assert!(!verify_proof("different-key", &challenge, &answer));
        assert!(!verify_proof(key, &"b".repeat(64), &answer));
        assert!(!verify_proof(
            key,
            &challenge,
            &json!({"engine":"tmodel-engine"})
        ));
    }

    #[test]
    fn reviewer_identity_is_private_stable_and_does_not_follow_symlinks() {
        use std::os::unix::fs::{symlink, PermissionsExt};
        let directory =
            std::env::temp_dir().join(format!("tmodel-review-{}", random_hex(16).unwrap()));
        let identity = reviewer_identity(&directory).unwrap();
        assert_eq!(reviewer_identity(&directory).unwrap(), identity);
        assert!(identity.starts_with("party:local:"));
        let path = directory.join("reviewer-id");
        assert_eq!(
            fs::metadata(&path).unwrap().permissions().mode() & 0o777,
            0o600
        );
        fs::set_permissions(&path, fs::Permissions::from_mode(0o644)).unwrap();
        assert!(reviewer_identity(&directory).is_err());
        fs::rename(&path, directory.join("original")).unwrap();
        symlink(directory.join("original"), &path).unwrap();
        assert!(reviewer_identity(&directory).is_err());
        fs::remove_dir_all(directory).unwrap();
    }

    #[test]
    fn an_unverified_port_receives_no_bearer_token() {
        use std::net::TcpListener;
        let listener = TcpListener::bind((Ipv4Addr::LOCALHOST, 0)).unwrap();
        let port = listener.local_addr().unwrap().port();
        let reader = std::thread::spawn(move || {
            let (mut socket, _) = listener.accept().unwrap();
            let mut bytes = [0; 2048];
            let size = socket.read(&mut bytes).unwrap();
            let request = String::from_utf8_lossy(&bytes[..size]).into_owned();
            assert!(request.starts_with("GET /host/health?challenge="));
            assert!(!request.contains("Authorization"));
            assert!(!request.contains("test-only"));
            socket
                .write_all(b"HTTP/1.0 200 OK\r\n\r\n{\"engine\":\"tmodel-engine\"}")
                .unwrap();
        });
        assert!(verify_engine(
            port,
            &HostCredentials {
                token: "test-only-token".into(),
                identity: "test-only-identity".into(),
            }
        )
        .is_err());
        reader.join().unwrap();
    }

    #[test]
    fn read_only_engine_declines_a_session_without_startup_retries() {
        use std::net::TcpListener;
        let listener = TcpListener::bind((Ipv4Addr::LOCALHOST, 0)).unwrap();
        let port = listener.local_addr().unwrap().port();
        let server = std::thread::spawn(move || {
            let (mut socket, _) = listener.accept().unwrap();
            let mut bytes = [0; 2048];
            assert!(socket.read(&mut bytes).unwrap() > 0);
            socket.write_all(b"HTTP/1.0 503 Service Unavailable\r\n\r\n{\"error\":{\"code\":\"workspace_failure\"}}").unwrap();
        });
        assert!(!verify_engine(
            port,
            &HostCredentials {
                token: "test-only-token".into(),
                identity: "test-only-identity".into(),
            }
        )
        .unwrap());
        server.join().unwrap();
    }

    #[test]
    fn webview_cannot_supply_paths_or_reviewer_identities() {
        assert!(serde_json::from_value::<HostProjectStep>(
            json!({"kind":"open-file","path":"/tmp/unchecked.yaml"})
        )
        .is_err());
        assert!(serde_json::from_value::<HostProjectStep>(json!({"kind":"create-project","from":{"source_file":"example.yaml","reviewer_id":"sponsor"}})).is_err());
        assert!(valid_model_id(&format!("project:{}", "a".repeat(32))));
        assert!(!valid_model_id("../../unopened.yaml"));
    }
}

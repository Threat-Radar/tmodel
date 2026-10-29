// tmodel desktop shell. One window; the TypeScript frontend talks to the local
// Python engine over its loopback API (ADR-0003). The app starts the bundled
// engine on launch and stops it on quit (#124).

mod engine;

use tauri::RunEvent;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .manage(engine::EngineState::default())
        .invoke_handler(tauri::generate_handler![engine::engine_process])
        .setup(|app| {
            engine::start(app.handle());
            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error while building tauri application")
        .run(|app, event| {
            if let RunEvent::Exit = event {
                engine::stop(app);
            }
        });
}

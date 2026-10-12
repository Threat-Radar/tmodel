// tmodel desktop shell. Slice 0: one window; the TypeScript frontend talks to the
// local Python engine over its loopback API (ADR-0003). No commands yet.

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

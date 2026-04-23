// Prevents additional console window on Windows in release
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::{Manager, WindowEvent};
use std::sync::Mutex;

pub struct AppState {
    pub dark_mode: Mutex<bool>,
}

fn main() {
    tauri::Builder::default()
        .manage(AppState {
            dark_mode: Mutex::new(true), // Default to dark mode
        })
        .setup(|app| {
            println!("TigerEx Users Desktop App starting...");
            Ok(())
        })
        .on_window_event(|window, event| {
            if let WindowEvent::CloseRequested { api, .. } = event {
                // Handle window close
                api.prevent_close();
                window.close().unwrap();
            }
        })
        .invoke_handler(tauri::generate_handler![
            toggle_theme,
            get_theme,
            get_platform_info
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

// Toggle Dark/Light Theme
#[tauri::command]
fn toggle_theme(state: tauri::State<AppState>) -> bool {
    let mut dark_mode = state.dark_mode.lock().unwrap();
    *dark_mode = !*dark_mode;
    println!("Theme toggled: {}", if *dark_mode { "Dark" } else { "Light" });
    *dark_mode
}

// Get Current Theme
#[tauri::command]
fn get_theme(state: tauri::State<AppState>) -> bool {
    let dark_mode = state.dark_mode.lock().unwrap();
    *dark_mode
}

// Get Platform Info (Windows, Mac, Linux)
#[tauri::command]
fn get_platform_info() -> String {
    #[cfg(target_os = "windows")]
    return "Windows".to_string();
    
    #[cfg(target_os = "macos")]
    return "Mac OS".to_string();
    
    #[cfg(target_os = "linux")]
    return "Linux".to_string();
    
    #[cfg(not(any(target_os = "windows", target_os = "macos", target_os = "linux")))]
    return "Unknown".to_string();
}
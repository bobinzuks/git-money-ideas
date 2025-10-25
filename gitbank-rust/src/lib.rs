#[cfg(target_arch = "wasm32")]
pub mod wasm_discovery;

#[cfg(target_arch = "wasm32")]
pub use wasm_discovery::*;

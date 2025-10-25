pub mod client;
pub mod training;

pub use client::AgentDBClient;
pub use training::{OpportunityData, train_on_opportunities, validate_training, extract_patterns};

pub mod model {
    use serde_derive::{Deserialize, Serialize};
    use serde_json::Value;

    // The structs for the database fields.
    #[derive(Serialize, Deserialize, Debug)]
    pub struct BeachHouse {
        pub id: String,
        pub title: String,
        pub event_start: String,
        pub event_end: String,
        pub event_repeat: String,
        pub reminder_minutes: i32,
        pub event_color: String,
        pub event_notes: String,
    }

    // #[derive(Serialize, Deserialize, Debug)]
    // pub struct Email {
    //     pub id: String,
    //     pub title: String,
    //     pub start: String,
    //     pub end: String,
    //     pub body: String,
    //     pub html_body: String,
    //     pub color: String,
    //     pub notes: String,
    // }
}
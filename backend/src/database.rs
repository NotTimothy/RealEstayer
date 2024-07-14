pub mod database {
    use tokio_stream::StreamExt;
    use futures::io::CopyBuf;
    use futures::stream::Collect;
    use mongodb::{bson::doc, Client, Collection, Cursor, Database};
    use crate::model::*;
    use titlecase::titlecase;

    // Database logic for the mongoDB instance in Rust.
    // Connects to MongoDB.
    pub async fn connect_to_db() -> Database {
        let client = Client::with_uri_str("mongodb://192.168.1.71:27017").await;
        let database = client.expect("Cant connect to database.").database("dommy-mommy");

        database
    }

    // Database logic for writing heroes.
    pub async fn write_approved_event_to_db(database: Database, data: model::Event)  {
        let collection = database.collection::<model::Event>("approved-event");

        let _ = collection.insert_one(data, None).await;
    }

    // Database logic for writing heroes.
    pub async fn write_pending_events_to_db(database: Database, data: model::Event)  {
        let collection = database.collection::<model::Event>("pending_event");

        let _ = collection.insert_one(data, None).await;
    }


    // Database logic for getting a specific hero.
    pub async fn get_approved_events_from_db(database: Database) -> Vec<model::Event> {
        let collection = database.collection::<model::Event>("approved-event");
        let mut cursor: Cursor<model::Event> = collection.find(None, None).await.unwrap();

        let mut events: Vec<model::Event> = Vec::new();

        while let Some(result) = cursor.try_next().await.unwrap() {
            events.push(result);
        }

        events
    }

    pub async fn get_pending_events_from_db(database: Database) -> Vec<model::Event> {
        let collection = database.collection::<model::Event>("pending-event");
        let mut cursor: Cursor<model::Event> = collection.find(None, None).await.unwrap();

        let mut events: Vec<model::Event> = Vec::new();

        while let Some(result) = cursor.try_next().await.unwrap() {
            events.push(result);
        }

        events
    }
}
CREATE TABLE counting_users ();
ALTER TABLE counting_users ADD COLUMN game_channel_id NUMERIC;
ALTER TABLE counting_users ADD COLUMN user_id NUMERIC;
ALTER TABLE counting_users ADD COLUMN total_numbers_counted INTEGER;
ALTER TABLE counting_users ALTER COLUMN game_channel_id SET NOT NULL;
ALTER TABLE counting_users ALTER COLUMN user_id SET NOT NULL;
ALTER TABLE counting_users ALTER COLUMN total_numbers_counted SET NOT NULL;
ALTER TABLE counting_users ADD CONSTRAINT _counting_users_game_channel_id_user_id_primary_key PRIMARY KEY ( game_channel_id , user_id );
ALTER TABLE counting_users ADD CONSTRAINT game_channel_id_fk FOREIGN KEY ( game_channel_id ) REFERENCES counting_channels ( channel_id ) MATCH SIMPLE ON DELETE CASCADE ON UPDATE CASCADE;
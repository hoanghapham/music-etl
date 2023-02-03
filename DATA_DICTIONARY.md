
- [msd schema](#msd-schema)
  - [msd.artists](#msdartists)
  - [msd.songs](#msdsongs)
- [mapped schema](#mapped-schema)
  - [mapped.songs](#mappedsongs)
  - [mapped.artists](#mappedartists)
  - [spotify.songs](#spotifysongs)
- [spotify schema](#spotify-schema)
  - [spotify.artists](#spotifyartists)
- [analytics schema](#analytics-schema)
  - [analytics.artists](#analyticsartists)
  - [analytics.songs](#analyticssongs)


## msd schema

### msd.artists
This table contains information about artists extracted from the Million Song Dataset.

| Field     | Data type             | Description                                     |
| --------- | --------------------- | ----------------------------------------------- |
| id        | VARCHAR(256) NOT NULL | ID of the artist in the MSD datase              |
| name      | VARCHAR(256)          | Name of the artist                              |
| location  | VARCHAR(MAX)          | Location of the artist                          |
| longitude | NUMERIC               | longitude of the artist                         |
| latitude  | NUMERIC               | latitude of the artists                         |
| tags      | SUPER                 | all tags attached to the artists on MusicBrainz |


### msd.songs
This table contains information about songs extracted from the Million Song Dataset.

| Field       | Description           | Description                                                                                                               |
| ----------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| id          | VARCHAR(256) NOT NULL | ID of the song in the MSD                                                                                                 |
| name        | VARCHAR(256)          | Name of the song                                                                                                          |
| release     | VARCHAR(256)          | Album the song was released in                                                                                            |
| genre       | VARCHAR(256)          | Tags reprenting the genre the song is classified in                                                                       |
| artist_id   | VARCHAR(256)          | ID of the artist.                                                                                                         |
| artist_name | VARCHAR(256)          | Name of the artist. One song in MSD can have multiple artists in one line, and together they can form one single "artist" |
| year        | INTEGER               | The year the song was released. 0 of not available.                                                                       |

## mapped schema
### mapped.songs

This table is used to map between MSD and Spotify songs.

| Field            | Data type    | Description                                                                        |
| ---------------- | ------------ | ---------------------------------------------------------------------------------- |
| msd_song_id      | VARCHAR(256) | ID of the MSD song                                                                 |
| spotify_song_ids | SUPER        | IDs of the Spotify songs matched with this MSD song by using the search endpoint |


### mapped.artists
This table is used to map between MSD and Spotify artists.

| Field              | Data Type    | Description                                                                   |
| ------------------ | ------------ | ----------------------------------------------------------------------------- |
| msd_artist_id      | VARCHAR(256) | ID of the artist extracted from MSD                                           |
| spotify_artist_ids | SUPER        | IDs of the Spotify artists matched with this artist via the search endpoint |


## spotify schema

### spotify.songs
This table contains detailed songs info fetched from Spotify

| Field             | Data type    | Description                                                                     |
| ----------------- | ------------ | ------------------------------------------------------------------------------- |
| id                | VARCHAR(256) | ID of the song on Spotify                                                       |
| name              | VARCHAR(256) | Name of the song on spotify                                                     |
| url               | VARCHAR(MAX) | Spotify URL of the song                                                         |
| external_ids      | SUPER        | IDs of the song on other music databases                                        |
| popularity        | NUMERIC      | Popularity metric of a song is calculated by Spotify                            |
| available_markets | SUPER        | Country codes of the countries that this song is available to listen on Spotify |
| album_id          | VARCHAR(256) | ID of the album associated with the song                                        |
| artists           | SUPER        | List of Spotify artists associated with the song                                |
| duration_ms       | INTEGER      | Duration of the song in milliseconds                                            |

### spotify.artists
| Field           | Data type    | Description                                                    |
| --------------- | ------------ | -------------------------------------------------------------- |
| id              | VARCHAR(256) | ID of the artist on Spotify                                    |
| name            | VARCHAR(256) | Name of the artist on Spotify                                  |
| url             | VARCHAR(MAX) | Spotify URL of the artist                                      |
| total_followers | INTEGER      | Number of Spotify users following this artist                  |
| popularity      | NUMERIC      | Popularity metric is calculated by Spotify                     |
| genres          | SUPER        | List of tags that represent the genres this artist performs in |

## analytics schema
### analytics.artists

This table contains combined artists information from both MSD and Spotify

| Field                   | Data type    |
| ----------------------- | ------------ |
| msd_artist_id           | VARCHAR(256) |
| msd_artist_name         | VARCHAR(256) |
| msd_location            | VARCHAR(MAX) |
| msd_latitude            | NUMERIC      |
| msd_longitude           | NUMERIC      |
| msd_tags                | SUPER        |
| spotify_artist_id       | VARCHAR(256) |
| spotify_artist_name     | VARCHAR(256) |
| spotify_artist_url      | VARCHAR(MAX) |
| spotify_total_followers | INTEGER      |
| spotify_genres          | SUPER        |

### analytics.songs

This table contains combined artists information from both MSD and Spotify

| Field              | Data type    |
| ------------------ | ------------ |
| msd_song_id        | VARCHAR(256) |
| msd_song_name      | VARCHAR(256) |
| msd_release        | VARCHAR(256) |
| msd_artist_name    | VARCHAR(256) |
| genre              | SUPER        |
| year               | INTEGER      |
| spotify_song_id    | VARCHAR(256) |
| spotify_song_name  | VARCHAR(256) |
| spotify_url        | VARCHAR(MAX) |
| spotify_popularity | NUMERIC      |
| duration_ms        | INTEGER      |
| album_id           |              |

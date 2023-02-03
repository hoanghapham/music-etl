-- Which artist has the highest song count, and longest average song duration?

select
	cast(artists.artist_name as varchar) as artist_name
    , count(songs.id) as songs_count
    , avg(duration_ms)/ 1000 / 60 as avg_songs_duration_mins
from spotify.songs as songs
, songs.artists as artists
group by 1
order by 3 desc
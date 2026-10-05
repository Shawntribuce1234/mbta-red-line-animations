# Reflection 
Shawn Tribuce

DS 3500

## Storm Impact
Both animations make the February 2026 blizzard impossible to miss. In Animation A, 
actual travel times drop sharply around February 20th to the 21st, only going half the normal travel time measuring around 950 seconds. 
This is probably because the MBTA was running so few trips that the ones that did run were shorter or incomplete. 
By February 23, actual travel time was around 1923 seconds, which is actually 
above the normal baseline trip for the train, which could mean the service was resuming but with significant delays.  In Animation B, 
the most visually striking moment is the bright white square appearing around
Andrew station on February 23–24, which could mean there were alot of people traveling when the train started to run again.

## Data Limitations
On storm days, the scheduled_travel_time was null for many rows which could hinder the accuracy of our data. In the cleaning step I dropped 
those null rows which could lead to underrepresentation of trips in my data. This could explain why the 
scheduled line in Animation A appears stable during the blizzard window.

## Layered Architecture
The layer separation made debugging the model way easier. When the daily_avg_travel keys 
were coming back as integers instead of strings, I could fix it entirely inside model.py 
without touching either animation file. 

## AI Usage
I used Claude to help debug my code when errors came up and to clean up my comments. 
Claude was helpful for catching things like the wrong URL format for the LAMP API and the 
missing pyarrow dependency. 
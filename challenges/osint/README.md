# OSINT Challenge: Where in the World?

## Setup Instructions

This challenge requires creating an image of a famous landmark with GPS metadata embedded.

### Steps to Create the Challenge Image

1. **Download a landmark image**
   - Choose a famous landmark (e.g., Eiffel Tower, Big Ben, Colosseum)
   - Download a high-quality image

2. **Add GPS metadata using exiftool**
   ```bash
   # Example for Eiffel Tower (Paris, France)
   exiftool -GPSLatitude="48.8584" -GPSLongitude="2.2945" \
            -GPSLatitudeRef="N" -GPSLongitudeRef="E" \
            -overwrite_original mystery_location.jpg
   ```

### Example Landmark Images

You can download images from Pexels (free to use):

**Eiffel Tower (Paris, France)**
- URL: https://images.pexels.com/photos/699466/pexels-photo-699466.jpeg
- GPS: 48.8584°N, 2.2945°E
- Flag: FLAG{PARIS_FRANCE_EIFFELTOWER}

**Big Ben (London, UK)**
- URL: https://images.pexels.com/photos/460672/pexels-photo-460672.jpeg
- GPS: 51.5007°N, 0.1246°W
- Flag: FLAG{LONDON_UK_BIGBEN}

**Colosseum (Rome, Italy)**
- URL: https://images.pexels.com/photos/2064827/pexels-photo-2064827.jpeg
- GPS: 41.8902°N, 12.4922°E
- Flag: FLAG{ROME_ITALY_COLOSSEUM}

### Creating the Image

```bash
# Download Big Ben image
wget -O mystery_location.jpg "https://images.pexels.com/photos/460672/pexels-photo-460672.jpeg?auto=compress&cs=tinysrgb&w=1200"

# Add GPS metadata
exiftool -GPSLatitude="51.5007" -GPSLongitude="0.1246" \
         -GPSLatitudeRef="N" -GPSLongitudeRef="W" \
         -overwrite_original mystery_location.jpg

# Verify metadata
exiftool mystery_location.jpg | grep GPS
```

### Solution

Participants should:
1. Extract EXIF data using `exiftool mystery_location.jpg`
2. Use reverse image search (Google Images, TinEye)
3. Identify the landmark visually
4. Format the flag: FLAG{LONDON_UK_BIGBEN}

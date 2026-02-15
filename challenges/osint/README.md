# OSINT Challenge: Where in the World?

## Setup Instructions

This challenge requires creating an image of a famous landmark with GPS metadata embedded.

### Dynamic Generation (Automated)
The `generate_team_files.py` script now handles this automatically:

1.  **Selects a Landmark**: Picks a random landmark (Eiffel Tower, Big Ben, etc.) based on Team ID.
2.  **Downloads Image**: Fetches the image from Wikimedia Commons.
3.  **Embeds GPS**: Uses `exiftool` to set the landmark's GPS coordinates.
4.  **Generates Dynamic Flag**: `HYVE_CTF{CITY_COUNTRY_LANDMARK_HASH}`.
5.  **Embeds Flag (Stego)**: Uses `steghide` to embed the flag into the image.
    -   **Password**: The GPS coordinates in the format `{lat:.2f}{lon:.2f}`.
    -   Example: If GPS is `48.86°N, 2.29°E`, the password is `48.862.29`.

### Solution

Participants should:
1.  **Extract EXIF data** using `exiftool mystery_location.jpg` to find the GPS coordinates.
2.  **Construct the password** from the coordinates (e.g., `48.862.29`).
3.  **Extract the hidden flag** using `steghide`:
    ```bash
    steghide extract -sf mystery_location.jpg -p "48.862.29"
    ```
4.  The extracted file (`flag.txt` or printed content) will contain the flag: `HYVE_CTF{PARIS_FRANCE_EIFFELTOWER_...}`.

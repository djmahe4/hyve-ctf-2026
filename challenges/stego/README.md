# Steganography Challenge: Secret Ingredient List

## Challenge Description
A secret list of ingredients is hidden in this bistro cat photo. It was embedded using steghide.
Participants are provided with a wordlist to help crack the password.

## Setup Instructions (Automated)
The `generate_team_files.py` script automatically:
1.  Creates a `cat.jpeg` image.
2.  Embeds the flag `HYVE_CTF{st3g0_cat_m4st3r}` using `steghide`.
3.  Generates a `wordlist.txt` containing the password (`meow`).

## Solution
1.  **Download the files** (`cat.jpeg` and `wordlist.txt`) from the CTFd challenge "Files" tab.
2.  **Crack the password** using `steghide` and the provided wordlist (or just guess 'meow' if checking the list).
    ```bash
    # Example using steghide-cracker or manual trying
    steghide extract -sf cat.jpeg -p meow
    ```
3.  **Read the extracted file** to find the flag: `HYVE_CTF{st3g0_cat_m4st3r}`.

# <p align="center">Kattis API</p>

<p align="center">
An interface to get your Kattis data, including your solved problems, rank and score!
</p>

## Setup

Install required dependencies in `requirements.txt`:

```
pip install -r requirements.txt
```

## kattis.user

Implementation of user related functionalities

### `class KattisUser(<username>, <password>)`

Constructs a `KattisUser` and sends a POST request to Kattis to authenticate.

#### `get_stats()`

Returns the user's Kattis rank and score.

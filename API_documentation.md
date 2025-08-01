# API documentation for YouTube to MP3/MP4 converter

## POST `/api/convert`
Converts a YouTube video to the selected format.

### Request body (JSON)

| Field     | Type     | Required | Description                                               |
|------------|----------|---------|-----------------------------------------------------|
| `url`      | string   | ✅       | Full YouTube link (Example: `https://www.youtube.com/watch?v=...`) |
| `format`   | string   | ✅       | Desired output format: `mp3` or `mp4`                                     |
| `resolution` | string | ❌       | Only for `mp4` format. Options: `144p`, `240p`, `360p`, `480p`, `720p`, `1080p`|

### Sample request

```json
{
  "url": "https://www.youtube.com/watch?v=...",
  "format": "mp4",
  "resolution": "720p"
}
```

### Success response
If the file was successfully converted and saved on the server:

```json
{
    "status": "success",
    "message": "Download complete",
    "filename": "File_name.mp4",
}
```

### Error response
If an error or exception occurs:

```json
{
    "status": "error",
    "message": "Error message"
}
```

## GET `/api/download/{filename}`
Downloads a converted MP3/MP4 file from the server.

### Parameters

| Parameter | Description |
|-----------|-------------|
|`filename` | Name of the file returned from `/api/convert` response|

### Success response
Returns the requested file as a download.

### Error response
Requested file doesn't exist:

```json
{
    "status": "error", 
    "message": "File not found"
}
```
## DELETE `/api/delete/{filename}`
Deletes a previously downloaded file from the server.

### Parameters

| Parameter | Description |
|-----------|-------------|
|`filename` | Name of the file returned by the `/api/convert` response|

### Success response
If the file was found and successfully deleted:

```json
{
    "status": "deleted"
}
```
If the file wasn't found (not treated as an error):

```json
{
    "status": "not found"
}
```

### Error response
If an error or exception occurs:

```json
{
    "status": "error", 
    "message": "Error message"
}
```

## GET `/api/logs`
Downloads a text file with full history of all conversions.

### Log format
```yaml
(ID, 'Title', 'Format', 'Date')
```
### Success response
Returns `logs.txt` as a file download.

### Error response
If an error or exception occurs:

```json
{
    "status": "error", 
    "message": "Error message"
}
```

## GET `/api/stats`
Returns server statistics in JSON format.

### Success response
Sample response:

```json
{
    "status": "success",
    "total_conversions": 50,
    "number_of_mp3": 40,
    "number_of_mp4": 10,
}
```
### Error response
If an error or exception occurs:

```json
{
    "status": "error", 
    "message": "Error message"
}
```


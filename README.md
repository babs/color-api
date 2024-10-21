# color-api

Color API is a simple FastAPI application that generates colored PNG images based on specified dimensions and a predefined environment-specified color.

## Configuration

- `COLOR`: Environment variable to set the color of the generated image. Accepts CSS color names or hex codes. Default is grey if not set or invalid.

## API Endpoints

- `GET /api/v1/png` or `GET /`: Generate a PNG image

  Query parameters:
     - `h`: Height of the image (default: 32, max: 1024)
     - `w`: Width of the image (default: 32, max: 1024)

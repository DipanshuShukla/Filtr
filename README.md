# Filtr

**Environment:** Python, Flask, SQL, JavaScript, Jinja2, HTML5, CSS

## About
For my CS50 Final Project, I created an image filter webapp.
This is a dynamically generated website using the flask framework for python.

## Image Filters
A software routine that changes the appearance of an image or part of an image by altering the shades and colors of the pixels in some manner.
Filters are used to increase brightness and contrast as well as to add a wide variety of textures, tones and special effects to a picture.

Prerequisites: python3, Flask, CS50 python library (for the sql)

To run it: `python app.py` or `flask run` in the code directory.

## Explanation
The user may login or register their account through the designated pages.
The users are then taken into the `/browse-images` route where the images uploaded by the user are displayed.
The user may then click the try button to go on to the next page to apply some filters.
When clicked on the try button, the user is taken into another webpage where the user then selects the filter to be applied using an intuitive user interface.
On the filter page, the user may then download the filtered image using a designated download button.

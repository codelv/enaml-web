# Pandas Dataframe Viewer

This is a simple interactive enaml app that loads a csv file using pandas.  The selection can be changed and the view will update in real time and show a loading indicator.

![image](https://user-images.githubusercontent.com/380158/51365747-db28e480-1aaf-11e9-8c8e-c274acbee85c.png)


All interaction is done on a single page through websockets.

To run

```bash
# install
pip install pandas tornado enaml-web

# cd to the example
python app.py

```

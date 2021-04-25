# Botokovich
A project to create a web app capable of generating music based on seed music that is input by the user.

![App img](https://bl3301files.storage.live.com/y4m9dDuqR0Tnr7JX3EZ7R4ABeTXmpzggQn6fzQGSixe0_e57WmsA7QIULCtdAcBTaQNb7FOg4WQz3MXt3Q5FD6WmJkZKJFmqRImfXQDyCLrOpxxi4jaKVFkWp1zUTbxRqZGNX4LH7Hrmxi26MI_gINAiHE64dSXKDe1vF-RgacU1aqL43DwsWQAhSmZVgLoaAMS?width=2876&height=934&cropmode=none)

Visit this [link](https://www.youtube.com/watch?v=HFZNpdqYKnU) to hear the midi of the following example.

![Generated music img](https://bl3301files.storage.live.com/y4m9dDuqR0Tnr7JX3EZ7R4ABeTXmpzggQn6fzQGSixe0_e57WmsA7QIULCtdAcBTaQNb7FOg4WQz3MXt3Q5FD6WmJkZKJFmqRImfXQDyCLrOpxxi4jaKVFkWp1zUTbxRqZGNX4LH7Hrmxi26MI_gINAiHE64dSXKDe1vF-RgacU1aqL43DwsWQAhSmZVgLoaAMS?width=2876&height=934&cropmode=none)

## Usage
Clone the repository and open two terminal windows.

Note: you may be required to create a Flat.io account 

To start the server:
1. Create the virtual environment: `conda env create -f environment.yml`.
2. Activate the virtual environment: `conda activate botokovich-app`.
2. Cd into the app folder and start the server: `uvicorn server:app --reload`.

To start the client:
1. In the other terminal window, cd into the client folder.
2. Install frontend dependencies: `npm install`.
3. Run the client: `npm start`.


This app was bootstrapped with [this](https://github.com/rcdilorenzo/ecce/tree/master/ecce).

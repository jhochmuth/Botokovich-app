# Botokovich
A project to create a web app capable of generating music based on seed music that is input by the user.

Visit this [link](https://www.youtube.com/watch?v=HFZNpdqYKnU) to hear the midi of the following example.

![Generated music img](https://github.com/jhochmuth/Botokovich/blob/master/data/generated_examples/exemplary_examples/chorales/sheetmusic_300hs_10bs_001lr_40e_0.png)

This app was bootstrapped with [this](https://github.com/rcdilorenzo/ecce/tree/master/ecce).

## Usage
Clone the repository and open two terminal windows.

To start the server:
1. Create the virtual environment: `conda env create -f environment.yml`.
2. Activate the virtual environment: `conda activate botokovich-app`.
2. Cd into the app folder and start the server: `uvicorn server:app --reload`.

To start the client:
1. In the other terminal window, cd into the client folder.
2. Install frontend dependencies: `npm install`.
3. Run the client: `npm start`.

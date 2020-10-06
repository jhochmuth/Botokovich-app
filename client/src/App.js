import React, { Component } from 'react';
import Embed from 'flat-embed';
import { Button, Slider, Typography } from '@material-ui/core'
import './App.css';

class App extends Component {
  state = {
    outputLength: 24
  }

  constructor(props) {
    super(props);
    this.flatEmbed = null;
  }

  componentDidMount() {
    const container = document.getElementById('flat-container');

    this.flatEmbed = new Embed(container, {
      score: '5eec27dee4645c2df0df0857',
      embedParams: {
        mode: 'edit',
        appId: '5ee199bd36e3a0440978997a',
        controlsPosition: 'top',
        parts: 'Piano',
        branding: false
      }
    });
  }

  async postMusicAndGenerate() {
    let xml = await this.flatEmbed.getMusicXML();
    let response = await fetch('/generate', {
      method: 'POST',
      body: JSON.stringify({xml, length: this.state.outputLength})
    });
    response = await response.json();

    await this.flatEmbed.loadMusicXML(response.data);
    this.flatEmbed.setDisplayedParts({parts: [0, 1]});
  }

  render() {
    return (
      <div className="App">
        <div id="flat-container" />
        <div id="settings-container">
        <Typography>Number of measures to generate:</Typography>
        <Slider
          value={this.state.outputLength}
          step={1}
          min={4}
          max={48}
          valueLabelDisplay="auto"
          onChange={(event, value) => this.setState({outputLength: value})}
        />
        <Button
          color="primary"
          variant="outlined"
          onClick={() => this.postMusicAndGenerate()}
        >
          Generate
        </Button>
        </div>
      </div>
    );
  }
}

export default App;

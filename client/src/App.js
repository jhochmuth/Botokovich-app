import React, { Component } from 'react';
import Embed from 'flat-embed';
import './App.css';

class App extends Component {
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
        controlsPosition: 'top'
      }
    });
  }

  async getGeneratedMusic() {
    let midi = await this.flatEmbed.getMIDI();
    let midiString = midi.toString();
    let response = await fetch('/generate/' + midiString);
    response = await response.json();
    console.log(response.data)
  }

  render() {
    return (
      <div className="App">
        <div id="flat-container" />
        <button onClick={() => this.getGeneratedMusic()}>Generate Music</button>
      </div>
    );
  }
}

export default App;

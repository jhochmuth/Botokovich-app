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
    let xml = await this.flatEmbed.getMusicXML();
    let response = await fetch('/generate', {
      method: 'POST',
      body: JSON.stringify(xml)
    });
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

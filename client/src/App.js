import React, { Component } from 'react';
import Embed from 'flat-embed';
import './App.css';

class App extends Component {
  constructor(props) {
    super(props);
    this.embed = null;
  }

  componentDidMount() {
    /*
    fetch('/api/verse/Genesis/1/1')
      .then(r => r.json())
      .then(data => this.setState({ text: data.text }));
    */
    const container = document.getElementById('flat-container');

    this.embed = new Embed(container, {
      score: '5eec27dee4645c2df0df0857',
      embedParams: {
        mode: 'edit',
        appId: '5ee199bd36e3a0440978997a',
        controlsPosition: 'top'
      }
    });
  }

  createMidi() {

  }

  render() {
    return (
      <div className="App">
        <div id="flat-container" />
        <button onClick={() => this.createMidi()}>Create midi</button>
      </div>
    );
  }
}

export default App;

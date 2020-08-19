import React, {Component} from 'react';
import './App.css';
import UserProfile from "./user/UserProfile";


class App extends Component {


  componentWillMount() {
    this.userProfile = UserProfile.load();
    if (this.userProfile === null) {
      this.props.history.push('/user/signin');
    }
  }

  render() {
    return <h1>
      Application is ready and you are logged in! { this.userProfile.email}
    </h1>
  }

}

// function App() {
//   return (
//     <div className="App">
//       <header className="App-header">
//         <img src={logo} className="App-logo" alt="logo" />
//         <p>
//           Edit <code>src/2211p.js</code> and save to reload.
//         </p>
//         <a
//           className="App-link"
//           href="https://reactjs.org"
//           target="_blank"
//           rel="noopener noreferrer"
//         >
//           Learn React
//         </a>
//       </header>
//     </div>
//   );
// }

export default App;

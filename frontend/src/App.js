import React, {Component} from 'react';
import {LinearProgress} from "@material-ui/core";
import './App.css';
import UserProfile from "./user/UserProfile";


class App extends Component {

  constructor(props) {
    super(props);
    this.state = { userProfile: null }
  }

  componentDidMount() {
    const userProfile = UserProfile.load();
    if (userProfile === null) {
      this.props.history.push('/user/signin');
    }
    this.setState({userProfile: userProfile})
  }

  render() {
    if (!this.state.userProfile) {
        return <div>
            <LinearProgress />
        </div>
    } else {
    return <h1>
      Application is ready and you are logged in! { this.state.userProfile.email}
    </h1>
    }
  }

}

export default App;

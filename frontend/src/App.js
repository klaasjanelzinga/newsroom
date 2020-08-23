import React, {Component} from 'react';
import {LinearProgress} from "@material-ui/core";
import './App.css';
import {ApiFetch} from "./ApiFetch"
import {withSnackbar} from "notistack";

class App extends Component {

  constructor(props) {
    super(props);
    this.state = { user: null }
    this.apiFetch = new ApiFetch(props)
    this.userProfile = this.apiFetch.userProfile
  }

  componentDidMount() {
    if (this.userProfile) {
      this.apiFetch.fetchAuthorized('user', (json) => {
        this.setState({user: json})
      })
    } else {
      this.props.history.push("/user/signin")
    }
  }

  render() {
    if (this.state.user == null) {
        return <div>
            <LinearProgress />
        </div>
    } else {
      return <h1>
        App is ready and you are logged in! { this.state.user.email}
      </h1>
    }
  }

}

export default withSnackbar(App);

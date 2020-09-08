import * as React from 'react';
import {LinearProgress} from "@material-ui/core";
import './App.css';
import {Api} from "./Api"
import {withSnackbar, WithSnackbarProps} from "notistack";
import {RouteComponentProps} from "react-router";
import UserProfile from "./user/UserProfile";
import News from "./news/news";

interface AppProps extends RouteComponentProps, WithSnackbarProps {
}

interface AppState {
    userProfile: UserProfile | null
}

class App extends React.Component<AppProps, AppState> {

    state: AppState = {
        userProfile: null
    }

    apiFetch: Api

    constructor(props: AppProps) {
        super(props);
        this.apiFetch = new Api(props)
    }

    componentDidMount() {
        const userProfile = UserProfile.load()
        if (!userProfile) {
            this.props.history.push("/user/signin")
        }
        this.setState({userProfile: userProfile})
    }

    render() {
        if (this.state.userProfile == null) {
            return <div>
                <LinearProgress/>
            </div>
        } else {
            return <News userProfile={this.state.userProfile}/>
        }
    }
}

export default withSnackbar(App);

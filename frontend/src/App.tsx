import * as React from 'react';
import {LinearProgress} from "@material-ui/core";
import './App.css';
import {ApiFetch} from "./ApiFetch"
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

    apiFetch: ApiFetch

    constructor(props: AppProps) {
        super(props);
        this.apiFetch = new ApiFetch(props)
    }

    componentDidMount() {
        const userProfile = UserProfile.load()
        this.setState({userProfile: userProfile})
        if (userProfile) {
            this.apiFetch.get<UserProfile>('/user')
                .then((response) => {
                    this.setState({userProfile: response[1]})
                })
                .catch(reason => console.error(reason))
        } else {
            this.props.history.push("/user/signin")
        }
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

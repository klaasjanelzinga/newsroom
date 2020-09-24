import * as React from 'react';
import {createStyles, LinearProgress, WithStyles, withStyles} from "@material-ui/core";
import './App.css';
import {Api} from "./Api"
import {withSnackbar, WithSnackbarProps} from "notistack";
import {RouteComponentProps} from "react-router";
import UserProfile from "./user/UserProfile";
import News, {NewsVariant} from "./news/news";
import {withRouter} from "react-router-dom";
import {WithAuthHandling, withAuthHandling} from "./WithAuthHandling";

const styles = createStyles({})

interface AppProps extends RouteComponentProps, WithSnackbarProps, WithAuthHandling, WithStyles<typeof styles> {
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
        this.apiFetch = new Api(this.props)
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
            return <div>
                <News userProfile={this.state.userProfile} variant={NewsVariant.NEWS}/>
            </div>
        }
    }
}

export default withStyles(styles)(withRouter(withSnackbar(withAuthHandling(App))))

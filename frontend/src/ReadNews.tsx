import * as React from 'react';
import {createStyles, LinearProgress, WithStyles, withStyles} from "@material-ui/core";
import './App.css';
import {Api} from "./Api"
import {withSnackbar, WithSnackbarProps} from "notistack";
import {RouteComponentProps} from "react-router";
import UserProfile from "./user/UserProfile";
import News, {NewsVariant} from "./news/news";
import {withRouter} from "react-router-dom";
import {withAuthHandling, WithAuthHandling} from "./WithAuthHandling";

const styles = createStyles({})

interface AppProps extends WithAuthHandling, RouteComponentProps, WithSnackbarProps, WithStyles<typeof styles> {
}

interface AppState {
    userProfile: UserProfile | null
}

class ReadNews extends React.Component<AppProps, AppState> {

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
            return <News userProfile={this.state.userProfile} variant={NewsVariant.READ_NEWS}/>
        }
    }
}

export default withStyles(styles)(withRouter(withSnackbar(withAuthHandling(ReadNews))))

import * as React from 'react';
import {createStyles, WithStyles, withStyles} from '@material-ui/core';
import {withSnackbar, WithSnackbarProps} from 'notistack';
import {RouteComponentProps, withRouter} from 'react-router-dom';
import HeaderBar from '../headerbar/HeaderBar';
import GoogleCard from './googlecard';
import UserProfile from './UserProfile';
import {Api} from "../Api";
import {UserProfileResponse} from "./model";
import queryString from 'query-string';


const styles = createStyles({
    card: {
        display: 'flex',
        width: '600px',
        margin: '10px',
    },
    details: {
        display: 'flex',
        flexDirection: 'column',
    },
    content: {
        flex: '2 0 auto',
    },
    cards: {
        padding: '10px',
        width: '100%',
        display: 'flex',
    },
    disclosure: {
        padding: '10px',
    },
    googleButton: {
        backgroundColor: 'lightgrey',
        padding: '2px',
    }
});

interface SigninProps extends WithStyles<typeof styles>, RouteComponentProps, WithSnackbarProps {
}

class SignIn extends React.Component<SigninProps> {

    apiFetch: Api
    redirect_to: string | null

    constructor(props: SigninProps) {
        super(props);
        this.apiFetch = new Api(props)
        this.redirect_to = queryString.parse(this.props.location.search).redirect_to as string || null
        if (this.redirect_to === this.props.location.pathname) {
            this.redirect_to = null
        }
    }

    validateSignInWithServer= (bearerToken: string):void => {
        this.apiFetch.post<UserProfileResponse>('/user/signup', null, bearerToken)
            .then((response) => {
                this.props.enqueueSnackbar('Succesfully signed in', {
                    variant: 'info',
                });
                const user_profile_response = response[1]
                user_profile_response.id_token = bearerToken
                UserProfile.save(response[1])
                if (response[0] === 200) {
                    this.props.history.push(this.redirect_to || '/')
                } else {
                    this.props.history.push('/user/needs-approval')
                }
            })
            .catch((reason) => console.error("IN ERROR validate signin", reason))
    }

    render() {
        const { classes } = this.props;
        return <div>
            <HeaderBar />

            <div className={classes.cards}>
                <GoogleCard
                    validateSignInWithServer={this.validateSignInWithServer}
                    >
                </GoogleCard>
            </div>
        </div>
    }
}

export default withStyles(styles)(withRouter(withSnackbar(SignIn)));


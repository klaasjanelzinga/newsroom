import * as React from 'react';
import {Card, CardContent, createStyles, Typography, WithStyles, withStyles} from '@material-ui/core';
import {withSnackbar, WithSnackbarProps} from 'notistack';
import {RouteComponentProps, withRouter} from 'react-router-dom';
import HeaderBar from '../headerbar/HeaderBar';
import UserProfile from './UserProfile';
import {Api} from "../Api";
import {UserProfileResponse} from "./model";
import queryString from 'query-string';
import {withAuthHandling, WithAuthHandling} from "../WithAuthHandling";
import {GoogleAuthHandling} from "../GoogleAuthHandling";


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

interface SigninProps extends WithAuthHandling, WithStyles<typeof styles>, RouteComponentProps, WithSnackbarProps {
}

class SignIn extends React.Component<SigninProps> {

    apiFetch: Api
    redirect_to: string | null
    authHandling: GoogleAuthHandling

    constructor(props: SigninProps) {
        super(props);
        this.apiFetch = new Api(props)
        this.authHandling = props.authHandling
        this.redirect_to = queryString.parse(this.props.location.search).redirect_to as string || null
        if (this.redirect_to === this.props.location.pathname) {
            this.redirect_to = null
        }
    }

    async signin() {
        try {
            const googleUser = await this.authHandling.signin()
            if (!googleUser) {
                this.props.enqueueSnackbar('Cannot signin with google', {
                    variant: 'warning',
                    autoHideDuration: 3000,
                });
                return
            }
            const response = await this.apiFetch.post<UserProfileResponse>('/user/signup', null)
            UserProfile.save(response[1])
            if (response[0] === 200) {
                this.props.history.push(this.redirect_to || '/')
            } else {
                this.props.history.push('/user/needs-approval')
            }
        } catch (error) {
            console.log(error)
            this.props.enqueueSnackbar('Cannot signin with google', {
                variant: 'warning',
                autoHideDuration: 3000,
            });
        }
    }

    render() {
        const {classes} = this.props;
        return <div>
            <HeaderBar/>

            <div className={classes.cards}>
                <Card className={classes.card}>
                    <div className={classes.details}>
                        <CardContent className={classes.content}>
                            <Typography component="h5" variant="h5">
                                Login using google - You can sign in to the newsroom using your google account.
                            </Typography>
                            <Typography variant="subtitle1" color="textSecondary">
                                If your account has already been approved you will be taken to the newsroom site.
                            </Typography>
                            <Typography variant="subtitle1" color="textSecondary">
                                If you do not have an account with newsroom, your account will have to be approved
                                by
                                the
                                moderator. This will typically take a few days.
                            </Typography>
                        </CardContent>
                        <div className={classes.disclosure}>
                            <Typography variant="subtitle2">
                                Newsroom will access the following data in your google profile:
                                <ul>
                                    <li>Your email address.</li>
                                    <li>Your given name as registered with Google.</li>
                                    <li>Your family name as registered with Google.</li>
                                </ul>

                                The data is only used on this site and will not be shared. By clicking on the login
                                button you acknowledge this.
                            </Typography>
                        </div>
                        <div className={classes.googleButton}>
                            <button onClick={() => this.signin()}>Sign in</button>
                        </div>
                    </div>
                </Card>
            </div>
        </div>
    }
}

export default withStyles(styles)(withRouter(withSnackbar(withAuthHandling(SignIn))))


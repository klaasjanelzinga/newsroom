import * as React from 'react';
import {Button, Card, CardContent, createStyles, Icon, Typography, WithStyles, withStyles} from '@material-ui/core';
import {withSnackbar, WithSnackbarProps} from 'notistack';
import {RouteComponentProps, withRouter} from 'react-router-dom';
import HeaderBar from '../headerbar/HeaderBar';
import queryString from 'query-string';
import {TokenBasedAuthenticator, withAuthHandling, WithAuthHandling} from "../WithAuthHandling";
import Grid from "@material-ui/core/Grid";
import TextField from "@material-ui/core/TextField";


const styles = createStyles({
    card: {
        display: 'flex',
        width: '600px',
        margin: '10px',
    },
    cards: {
        padding: '10px',
        width: '100%',
    },
    saveButton: {
        marginLeft: '8px',
    },
    signUpButton: {
        marginLeft: '8px',
    },
    buttonBar: {
        fontSize: '13px',
        backgroundColor: 'lightgrey',
        padding: '8px',
        marginTop: '20px',
    },
});

interface SignInProps extends WithAuthHandling, WithStyles<typeof styles>, RouteComponentProps, WithSnackbarProps {
}

interface SignInState {
    email_address: string;
    password: string;
}

class SignIn extends React.Component<SignInProps, SignInState> {

    redirect_to: string | null
    authHandling: TokenBasedAuthenticator

    constructor(props: SignInProps) {
        super(props);
        this.state = {
            email_address: this.props.authHandling.user_information?.email_address || '',
            password: '',
        }
        this.authHandling = props.authHandling
        this.redirect_to = queryString.parse(this.props.location.search).redirect_to as string || null
        if (this.redirect_to === this.props.location.pathname) {
            this.redirect_to = null
        }

    }

    async sign_in(): Promise<void> {
        try {
            const sign_in_result = await this.authHandling.sign_in(this.state.email_address, this.state.password)
            if (!sign_in_result.success) {
                this.setState({password: ""})
                this.props.enqueueSnackbar(`Sign in failed: ${sign_in_result.reason || "Unknown"}`, {
                    variant: 'warning',
                    autoHideDuration: 3000,
                });
                return Promise.resolve()
            }
            if (this.authHandling.user_information?.is_approved) {
                this.props.history.push(this.redirect_to || '/')
            } else {
                this.props.history.push('/user/needs-approval')
            }
        } catch (error) {
            this.props.enqueueSnackbar('Cannot signin', {
                variant: 'warning',
                autoHideDuration: 3000,
            });
        }
        return Promise.resolve()
    }

    render(): JSX.Element {
        const {classes} = this.props;
        return <div>
            <HeaderBar/>

            <div className={classes.cards}>
                <Card className={classes.card}>
                    <CardContent>
                        <Grid container>
                            <Grid item xs={12}>
                                <Typography component="h5" variant="h5">
                                    Sign into your newsroom:
                                </Typography>
                            </Grid>
                            <Grid item xs={12}>
                                <TextField
                                    required
                                    id="email"
                                    name="email"
                                    label="Email address"
                                    fullWidth
                                    value={this.state.email_address}
                                    onChange={(e): void  => this.setState({email_address: e.currentTarget.value})}
                                    autoComplete="username"
                                />
                            </Grid>
                            <Grid item xs={12}>
                                <TextField
                                    required
                                    id="password"
                                    name="password"
                                    label="Password"
                                    type="password"
                                    onChange={(e): void => this.setState({password: e.currentTarget.value})}
                                    fullWidth
                                    value={this.state.password}
                                    autoComplete="password"
                                />
                            </Grid>
                            <Grid item xs={12}>
                                <div className={classes.buttonBar}>
                                    <Button
                                        variant="contained"
                                        color="primary"
                                        className={classes.saveButton}
                                        onClick={async (): Promise<void> => await this.sign_in()}
                                        endIcon={<Icon>login</Icon>}>
                                        Login
                                    </Button>
                                    <Button
                                        variant="contained"
                                        color="default"
                                        className={classes.signUpButton}
                                        onClick={(): void => this.props.history.push('/user/signup')}
                                        endIcon={<Icon>account_box</Icon>}>
                                        OR Sign up ...
                                    </Button>
                                </div>
                            </Grid>
                        </Grid>
                    </CardContent>
                </Card>
            </div>
        </div>
    }
}

export default withStyles(styles)(withRouter(withSnackbar(withAuthHandling(SignIn))))


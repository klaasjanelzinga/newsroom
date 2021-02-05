import * as React from 'react';
import {Button, Card, CardContent, createStyles, Icon, Typography, WithStyles, withStyles} from '@material-ui/core';
import {withSnackbar, WithSnackbarProps} from 'notistack';
import {RouteComponentProps, withRouter} from 'react-router-dom';
import HeaderBar from '../headerbar/HeaderBar';
import {Api} from "../Api";
import {SignInResult, TokenBasedAuthenticator, withAuthHandling, WithAuthHandling} from "../WithAuthHandling";
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

interface SignUpProps extends WithAuthHandling, WithStyles<typeof styles>, RouteComponentProps, WithSnackbarProps {
}

interface SignUpState {
    email_address: string
    password: string
    password_repeated: string
}

class SignUp extends React.Component<SignUpProps, SignUpState> {

    apiFetch: Api
    authHandling: TokenBasedAuthenticator

    constructor(props: SignUpProps) {
        super(props);
        this.apiFetch = new Api(props)
        this.authHandling = props.authHandling
        this.state = {
            email_address: this.props.authHandling.user_information?.email_address || '',
            password: '',
            password_repeated: ''
        }
    }

    async sign_up(): Promise<void> {
        try {
            const sign_in_result: SignInResult = await this.authHandling.sign_up(
                this.state.email_address, this.state.password, this.state.password_repeated
            )
            if (!sign_in_result.success) {
                this.setState({
                    password: "",
                    password_repeated: "",
                })
                this.props.enqueueSnackbar(`Sign up failed: ${sign_in_result.reason || "unknown"}`, {
                    variant: 'warning',
                    autoHideDuration: 3000,
                });
                return Promise.resolve()
            }
            if (this.authHandling.user_information?.is_approved) {
                this.props.history.push('/')
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

    render() {
        const {classes} = this.props;
        return <div>
            <HeaderBar/>

            <div className={classes.cards}>
                <Card className={classes.card}>
                    <CardContent>
                        <Grid container>
                            <Grid item xs={12}>
                                <Typography component="h5" variant="h5">
                                    Start the signing up process for newsroom:
                                </Typography>
                            </Grid>
                            <Grid item xs={12}>
                                <TextField
                                    required
                                    id="email"
                                    name="email"
                                    label="Email address"
                                    fullWidth
                                    onChange={(e) => this.setState({email_address: e.currentTarget.value})}
                                    value={this.state.email_address}
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
                                    onChange={(e) => this.setState({password: e.currentTarget.value})}
                                    value={this.state.password}
                                    fullWidth
                                    autoComplete="password"
                                />
                            </Grid>
                            <Grid item xs={12}>
                                <TextField
                                    required
                                    id="repeated_password"
                                    name="repeated_password"
                                    label="Repeat password"
                                    type="password"
                                    onChange={(e) => this.setState({password_repeated: e.currentTarget.value})}
                                    value={this.state.password_repeated}
                                    fullWidth
                                    autoComplete="password"
                                />
                            </Grid>
                            <Grid item xs={12}>
                                <div className={classes.buttonBar}>
                                    <Button
                                        variant="contained"
                                        color="primary"
                                        className={classes.saveButton}
                                        onClick={async () => await this.sign_up()}
                                        endIcon={<Icon>login</Icon>}>
                                        Sign up
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

export default withStyles(styles)(withRouter(withSnackbar(withAuthHandling(SignUp))))


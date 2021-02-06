import * as React from 'react';
import {Button, Card, CardContent, createStyles, Typography, WithStyles, withStyles} from '@material-ui/core';
import {withSnackbar, WithSnackbarProps} from 'notistack';
import {RouteComponentProps, withRouter} from 'react-router-dom';
import HeaderBar from '../headerbar/HeaderBar';
import {Api} from "../Api";
import {TokenBasedAuthenticator, withAuthHandling, WithAuthHandling} from "../WithAuthHandling";
import Grid from "@material-ui/core/Grid";
import TextField from "@material-ui/core/TextField";
import LockIcon from "@material-ui/icons/Lock"


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

interface ChangePasswordAttrs extends WithAuthHandling, WithStyles<typeof styles>, RouteComponentProps, WithSnackbarProps {
}

interface ChangePasswordState {
    email_address: string
    current_password: string
    new_password: string
    new_password_repeated: string
}

class ChangePassword extends React.Component<ChangePasswordAttrs, ChangePasswordState> {

    apiFetch: Api
    authHandling: TokenBasedAuthenticator

    constructor(props: ChangePasswordAttrs) {
        super(props);
        this.apiFetch = new Api(props)
        this.authHandling = props.authHandling
        this.state = {
            email_address: this.props.authHandling.user_information?.email_address || '',
            current_password: '',
            new_password: '',
            new_password_repeated: ''
        }
    }

    async change_password(): Promise<void> {
        try {
            const sign_in_result = await this.authHandling.change_password(
                this.state.email_address, this.state.current_password, this.state.new_password, this.state.new_password_repeated
            )
            if (!sign_in_result.success) {
                this.setState({
                    new_password: "",
                    new_password_repeated: "",
                    current_password: ""
                })
                this.props.enqueueSnackbar(`Changing of password failed: ${sign_in_result.reason || "Unknwon"}`, {
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
            this.props.enqueueSnackbar("Password changed", {
                variant: 'info',
                autoHideDuration: 3000,
            });
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
                                    Change your password for newsroom:
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
                                    label="Current password"
                                    type="password"
                                    onChange={(e) => this.setState({current_password: e.currentTarget.value})}
                                    value={this.state.current_password}
                                    fullWidth
                                    autoComplete="current-password"
                                />
                            </Grid>
                            <Grid item xs={12}>
                                <TextField
                                    required
                                    id="new_password"
                                    name="password"
                                    label="New password"
                                    type="password"
                                    onChange={(e) => this.setState({new_password: e.currentTarget.value})}
                                    value={this.state.new_password}
                                    fullWidth
                                    autoComplete="new-password"
                                />
                            </Grid>
                            <Grid item xs={12}>
                                <TextField
                                    required
                                    id="new_repeated_password"
                                    name="new_repeated_password"
                                    label="Repeat password"
                                    type="password"
                                    onChange={(e) => this.setState({new_password_repeated: e.currentTarget.value})}
                                    value={this.state.new_password_repeated}
                                    fullWidth
                                    autoComplete="new-password"
                                />
                            </Grid>
                            <Grid item xs={12}>
                                <div className={classes.buttonBar}>
                                    <Button
                                        variant="contained"
                                        color="primary"
                                        className={classes.saveButton}
                                        onClick={async () => await this.change_password()}
                                        >
                                        Change password
                                        <LockIcon/>
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

export default withStyles(styles)(withRouter(withSnackbar(withAuthHandling(ChangePassword))))


import * as React from "react"
import { Button, Card, CardContent, createStyles, Icon, Typography, WithStyles, withStyles } from "@material-ui/core"
import { withSnackbar, WithSnackbarProps } from "notistack"
import { RouteComponentProps, withRouter } from "react-router-dom"
import HeaderBar from "../headerbar/HeaderBar"
import { TokenBasedAuthenticator, withAuthHandling, WithAuthHandling } from "../WithAuthHandling"
import Grid from "@material-ui/core/Grid"
import TextField from "@material-ui/core/TextField"
import { Api } from "../Api"

const styles = createStyles({
    card: {
        display: "flex",
        width: "600px",
        margin: "10px",
    },
    cards: {
        padding: "10px",
        width: "100%",
    },
    saveButton: {
        marginLeft: "8px",
    },
    signUpButton: {
        marginLeft: "8px",
    },
    buttonBar: {
        fontSize: "13px",
        backgroundColor: "lightgrey",
        padding: "8px",
        marginTop: "20px",
    },
})

interface TOTPVerificationProps
    extends WithAuthHandling,
        WithStyles<typeof styles>,
        RouteComponentProps,
        WithSnackbarProps {}

interface TOTPVerificationState {
    totp_value: string
    totp_backup_code: string
}

class TOTPVerification extends React.Component<TOTPVerificationProps, TOTPVerificationState> {
    authHandling: TokenBasedAuthenticator
    api: Api

    constructor(props: TOTPVerificationProps) {
        super(props)
        this.state = {
            totp_value: "",
            totp_backup_code: "",
        }
        this.authHandling = props.authHandling
        this.api = new Api(props)
    }

    async otp_login(): Promise<void> {
        try {
            const result = await this.authHandling.totp_verification(this.state.totp_value)
            if (result.success) {
                this.props.history.push("/")
            } else {
                this.props.enqueueSnackbar(`Token verification failed`, {
                    variant: "warning",
                    autoHideDuration: 3000,
                })
            }
        } catch (error) {
            this.props.enqueueSnackbar("Cannot verify the token", {
                variant: "warning",
                autoHideDuration: 3000,
            })
        }
        return Promise.resolve()
    }

    async use_totp_backup_code(): Promise<void> {
        try {
            const result = await this.authHandling.use_totp_backup_code(this.state.totp_backup_code)
            if (result.success) {
                this.props.history.push("/")
            } else {
                this.props.enqueueSnackbar(`Backup code verification failed`, {
                    variant: "warning",
                    autoHideDuration: 3000,
                })
            }
        } catch (error) {
            this.props.enqueueSnackbar("Cannot verify the token", {
                variant: "warning",
                autoHideDuration: 3000,
            })
        }
        return Promise.resolve()
    }

    render(): JSX.Element {
        const { classes } = this.props
        return (
            <div>
                <HeaderBar />

                <div className={classes.cards}>
                    <Card className={classes.card}>
                        <CardContent>
                            <Grid container>
                                <Grid item xs={12}>
                                    <Typography component="h5" variant="h5">
                                        Use your authenticator to enter the token:
                                    </Typography>
                                </Grid>
                                <Grid item xs={12}>
                                    <TextField
                                        required
                                        label="Token value"
                                        fullWidth
                                        value={this.state.totp_value}
                                        onChange={(e): void => this.setState({ totp_value: e.currentTarget.value })}
                                    />
                                </Grid>
                                <Grid item xs={12}>
                                    <div className={classes.buttonBar}>
                                        <Button
                                            variant="contained"
                                            color="primary"
                                            className={classes.saveButton}
                                            onClick={async (): Promise<void> => await this.otp_login()}
                                            endIcon={<Icon>login</Icon>}
                                        >
                                            Verify
                                        </Button>
                                    </div>
                                </Grid>
                            </Grid>
                        </CardContent>
                    </Card>
                    <Card className={classes.card}>
                        <CardContent>
                            <Grid container>
                                <Grid item xs={12}>
                                    <Typography>
                                        Use a backup code to login. Note a backup code can only be used once!
                                    </Typography>
                                </Grid>
                                <Grid item xs={12}>
                                    <TextField
                                        required
                                        label="Backup token"
                                        fullWidth
                                        value={this.state.totp_backup_code}
                                        onChange={(e): void =>
                                            this.setState({ totp_backup_code: e.currentTarget.value })
                                        }
                                    />
                                </Grid>
                                <Grid item xs={12}>
                                    <div className={classes.buttonBar}>
                                        <Button
                                            variant="contained"
                                            onClick={async (): Promise<void> => await this.use_totp_backup_code()}
                                        >
                                            Use code
                                        </Button>
                                    </div>
                                </Grid>
                            </Grid>
                        </CardContent>
                    </Card>
                </div>
            </div>
        )
    }
}

export default withStyles(styles)(withRouter(withSnackbar(withAuthHandling(TOTPVerification))))

import * as React from "react"
import { Button, Card, CardContent, createStyles, Typography, WithStyles, withStyles } from "@material-ui/core"
import { withSnackbar, WithSnackbarProps } from "notistack"
import { RouteComponentProps, withRouter } from "react-router-dom"
import { Api } from "../Api"
import { TokenBasedAuthenticator, withAuthHandling, WithAuthHandling } from "../WithAuthHandling"
import Grid from "@material-ui/core/Grid"
import TextField from "@material-ui/core/TextField"
import { ConfirmTotpResponse, OTPRegistrationResponse, UserResponse } from "./model"
import QRCode from "qrcode"

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

interface ChangeTotpAttrs extends WithAuthHandling, WithStyles<typeof styles>, RouteComponentProps, WithSnackbarProps {}

interface ChangeTotpState {
    email_address: string
    totp_enabled: boolean
    generated_secret: string | null
    uri: string | null
    backup_codes: string[]
    totp_value: string | null
}

class ChangeTotp extends React.Component<ChangeTotpAttrs, ChangeTotpState> {
    api: Api
    authHandler: TokenBasedAuthenticator
    qrcode_element: HTMLCanvasElement | null = null

    constructor(props: ChangeTotpAttrs) {
        super(props)
        this.api = new Api(props)
        this.authHandler = props.authHandling

        this.state = {
            email_address: this.props.authHandling.user_information?.email_address || "",
            totp_enabled: this.props.authHandling.user_information?.totp_enabled || false,
            uri: null,
            generated_secret: null,
            backup_codes: [],
            totp_value: null,
        }
    }

    async start_totp_registration(): Promise<void> {
        this.api
            .post<OTPRegistrationResponse>("/user/start-totp-registration", JSON.stringify({}))
            .then((otpStartResponse) => {
                if (otpStartResponse[0] === 200) {
                    this.setState({
                        generated_secret: otpStartResponse[1].generated_secret,
                        uri: otpStartResponse[1].uri,
                        backup_codes: otpStartResponse[1].backup_codes,
                    })
                    QRCode.toCanvas(this.qrcode_element, otpStartResponse[1].uri)
                }
            })
            .catch((reason) => console.log(reason))
        return Promise.resolve()
    }

    async confirm_totp(): Promise<void> {
        this.api
            .post<ConfirmTotpResponse>(
                "/user/confirm-totp",
                JSON.stringify({
                    totp_value: this.state.totp_value,
                })
            )
            .then(async (confirmResponse) => {
                if (confirmResponse[0] === 200) {
                    if (confirmResponse[1].otp_confirmed) {
                        await this.authHandler.sign_out()
                        this.props.enqueueSnackbar(`TOTP successfully enabled, please sign in again.`, {
                            variant: "info",
                            autoHideDuration: 1500,
                        })
                        this.props.history.push("/user/signin")
                    } else {
                        this.props.enqueueSnackbar(`TOTP code not verified. Please try again`, {
                            variant: "info",
                            autoHideDuration: 1500,
                        })
                    }
                }
            })
            .catch((reason) => console.log(reason))
        return Promise.resolve()
    }

    async disable_totp(): Promise<void> {
        this.api
            .post<UserResponse>("/user/disable-totp", JSON.stringify({}))
            .then(async (userResponse) => {
                if (userResponse[0] === 200) {
                    await this.authHandler.sign_out()
                    this.props.enqueueSnackbar(`Please sign in again`, {
                        variant: "info",
                        autoHideDuration: 1500,
                    })
                    this.props.history.push("/user/signin")
                }
            })
            .catch((reason) => console.log(reason))
        return Promise.resolve()
    }

    render(): JSX.Element {
        const { classes } = this.props
        return (
            <div>
                <div className={classes.cards}>
                    <Card className={classes.card}>
                        <CardContent>
                            <Grid container>
                                <Grid item xs={12}>
                                    <Typography component="h5" variant="h5">
                                        Change your 2FA (TOTP) settings for newsroom:
                                    </Typography>
                                </Grid>
                                {!this.state.totp_enabled && (
                                    <Grid item xs={12}>
                                        <div className={classes.buttonBar}>
                                            <Button
                                                variant="contained"
                                                color="primary"
                                                disabled={this.state.generated_secret !== null}
                                                className={classes.saveButton}
                                                onClick={async (): Promise<void> =>
                                                    await this.start_totp_registration()
                                                }
                                            >
                                                Enable 2FA
                                            </Button>
                                        </div>
                                    </Grid>
                                )}
                                {!this.authHandler.user_information?.totp_enabled && (
                                    <Grid item xs={12}>
                                        <canvas
                                            id={"qrcode"}
                                            height={"200px"}
                                            width={"200px"}
                                            ref={(t: HTMLCanvasElement): HTMLCanvasElement => (this.qrcode_element = t)}
                                        />
                                    </Grid>
                                )}
                                {this.state.generated_secret && (
                                    <Grid container>
                                        <Grid item sm={12}>
                                            Scan the QR-code with your authenticator app or use the secret{" "}
                                            <pre>{this.state.generated_secret}</pre>
                                            to seed the authenticator app (manually).
                                        </Grid>
                                        <Grid item sm={12}>
                                            Keep these backup codes in a safe place:
                                            <pre>
                                                {this.state.backup_codes.map((code) => (
                                                    <div key={code}>{code}</div>
                                                ))}
                                            </pre>
                                        </Grid>
                                        <Grid item sm={12}>
                                            <Grid item sm={6}>
                                                <TextField
                                                    required
                                                    label="Enter token from the authenticator"
                                                    onChange={(e): void =>
                                                        this.setState({ totp_value: e.currentTarget.value })
                                                    }
                                                    fullWidth
                                                    value={this.state.totp_value}
                                                />
                                                <Button
                                                    variant="contained"
                                                    onClick={async (): Promise<void> => await this.confirm_totp()}
                                                >
                                                    Confirm
                                                </Button>
                                            </Grid>
                                        </Grid>
                                    </Grid>
                                )}
                                {this.state.totp_enabled && (
                                    <Grid item xs={12}>
                                        <div className={classes.buttonBar}>
                                            <Button
                                                variant="contained"
                                                color="primary"
                                                className={classes.saveButton}
                                                onClick={async (): Promise<void> => await this.disable_totp()}
                                            >
                                                Disable 2FA
                                            </Button>
                                        </div>
                                    </Grid>
                                )}
                            </Grid>
                        </CardContent>
                    </Card>
                </div>
            </div>
        )
    }
}

export default withStyles(styles)(withRouter(withSnackbar(withAuthHandling(ChangeTotp))))

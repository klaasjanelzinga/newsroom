import * as React from "react"
import { withSnackbar, WithSnackbarProps } from "notistack"
import { RouteComponentProps, withRouter } from "react-router-dom"
import HeaderBar from "../headerbar/HeaderBar"
import { Button, createStyles, Icon, Typography, WithStyles } from "@material-ui/core"
import withStyles from "@material-ui/core/styles/withStyles"
import { withAuthHandling, WithAuthHandling } from "../WithAuthHandling"

const styles = createStyles({
    googleButton: {
        margin: "10px",
    },
    signoutForm: {
        margin: "5px",
    },
})

interface SignoutProps extends RouteComponentProps, WithSnackbarProps, WithAuthHandling, WithStyles<typeof styles> {}

class SignOut extends React.Component<SignoutProps> {
    async logout(): Promise<void> {
        await this.props.authHandling.sign_out()
        this.props.enqueueSnackbar("You were signed out.", {
            variant: "info",
        })
        this.props.history.push("/user/signin")
        return Promise.resolve()
    }

    render(): JSX.Element {
        const { classes } = this.props
        return (
            <div>
                <HeaderBar />
                <div className={classes.signoutForm}>
                    <Typography component="h5" variant="h5">
                        Logout off the newsroom site.
                    </Typography>
                    <Typography variant="subtitle1" color="textSecondary">
                        <Button
                            onClick={async (): Promise<void> => this.logout()}
                            color="primary"
                            endIcon={<Icon>logout</Icon>}
                        >
                            Logout from newsroom
                        </Button>
                    </Typography>
                </div>
            </div>
        )
    }
}

export default withStyles(styles)(withRouter(withSnackbar(withAuthHandling(SignOut))))

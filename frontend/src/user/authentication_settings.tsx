import {withAuthHandling, WithAuthHandling} from "../WithAuthHandling";
import {createStyles, withStyles, WithStyles} from "@material-ui/core";
import {RouteComponentProps, withRouter} from "react-router-dom";
import {withSnackbar, WithSnackbarProps} from "notistack";
import ChangePassword from "./change_password"
import Change2fa from "./change_2fa"
import * as React from "react";

const styles = createStyles({
    card: {
        display: 'flex',
        width: '600px',
        margin: '10px',
    },
})

interface AuthenticationSettings extends WithAuthHandling, WithStyles<typeof styles>, RouteComponentProps, WithSnackbarProps {
}

interface AuthenticationSettingsState {
}

class AuthenticationSettings extends React.Component<AuthenticationSettings, AuthenticationSettingsState> {

    render(): JSX.Element {
        return <div>
            <ChangePassword />
            <Change2fa />
        </div>

    }
}

export default withStyles(styles)(withRouter(withSnackbar(withAuthHandling(AuthenticationSettings))))


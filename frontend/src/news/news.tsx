import * as React from "react";
import {createStyles, Typography, WithStyles} from "@material-ui/core";
import {RouteComponentProps, withRouter} from "react-router-dom";
import {withStyles} from "@material-ui/core/styles";
import UserProfile from "../user/UserProfile";
import HeaderBar from "../headerbar/HeaderBar";
import Header from "../user/header";

const styles = createStyles({});

export interface NewsProps extends RouteComponentProps, WithStyles<typeof styles> {
    userProfile: UserProfile
}


const News: React.FunctionComponent<NewsProps> = (props) => {
    return <div>
        <HeaderBar />
        <Header title={'News'} />
        <Typography onClick={() => props.history.push('/')}
                    variant="h6" color="inherit" noWrap>
            for {props.userProfile.email}
        </Typography>

    </div>
}

export default withStyles(styles)(withRouter(News));

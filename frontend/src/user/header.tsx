import * as React from "react";
import {createStyles, Typography, withStyles, WithStyles} from "@material-ui/core";

const styles = createStyles({
        header: {
            margin: "10px",
            borderBottom: 'lightgrey',
            borderBottomStyle: 'solid',
            borderBottomWidth: '1px',
        }
    }
)

interface HeaderProps extends WithStyles<typeof styles> {
    title: string;
}


const Header: React.FunctionComponent<HeaderProps> = (props: HeaderProps) => {
    const {classes} = props
    return <Typography variant="h4" className={classes.header} color="inherit" noWrap>
        {props.title}
    </Typography>
}

export default withStyles(styles)(Header)
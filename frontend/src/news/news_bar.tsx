import * as React from "react";
import {Button, createStyles, WithStyles, withStyles} from "@material-ui/core";
import RefreshIcon from "@material-ui/icons/Refresh";

const styles = createStyles({
    newsbar: {
        textAlign: "right",
        padding: "5px",
    },
    button: {}
})

interface NewsBarProps extends WithStyles<typeof styles> {
    refresh: () => void
}

const NewsBar: React.FunctionComponent<NewsBarProps> = (props: NewsBarProps) => {
    const {classes} = props
    return <div className={classes.newsbar}>
        <Button size="small"
                variant="outlined"
                onClick={props.refresh}
                className={classes.button}>
            <RefreshIcon />
        </Button>
    </div>

}

export default withStyles(styles)(NewsBar)
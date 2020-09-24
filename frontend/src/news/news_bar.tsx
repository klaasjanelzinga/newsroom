import * as React from "react";
import {Button, createStyles, WithStyles, withStyles} from "@material-ui/core";
import RefreshIcon from "@material-ui/icons/Refresh";
import {ArrowDownward, ArrowUpward} from "@material-ui/icons";

const styles = createStyles({
    newsbar: {
        textAlign: "right",
        padding: "5px",
    },
    button: {}
})

interface NewsBarProps extends WithStyles<typeof styles> {
    refresh: () => void
    next: () => void
    previous: () => void
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
        <Button size="small"
                variant="outlined"
                onClick={props.previous}
                className={classes.button}>
            <ArrowUpward />
        </Button>
        <Button size="small"
                variant="outlined"
                onClick={props.next}
                className={classes.button}>
            <ArrowDownward />
        </Button>
    </div>

}

export default withStyles(styles)(NewsBar)
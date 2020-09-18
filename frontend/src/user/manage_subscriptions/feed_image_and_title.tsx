import * as React from "react";
import {createStyles, WithStyles} from "@material-ui/core";
import {RouteComponentProps, withRouter} from "react-router-dom";
import {Feed} from "../model";
import {withStyles} from "@material-ui/core/styles";

const styles = createStyles({
    feedTitleAndImage: {
    },
    image: {
        height: "25px",
        width: "25px",
        textAlign: "center",
        verticalAlign: "middle",
    },
    text: {
        paddingLeft: "5px",
    },
});

export interface FeedProps extends RouteComponentProps, WithStyles<typeof styles> {
    feed: Feed
}


const ImageAndTitle: React.FunctionComponent<FeedProps> = (props) => {
    const {classes} = props
    return <div className={classes.feedTitleAndImage}>
        {props.feed.image_link && <a href={props.feed.image_link}>
            <img className={classes.image}
                 src={props.feed.image_url}
                 alt={props.feed.image_title}
                 title={props.feed.image_title}/>
        </a>}
        <span className={classes.text}>
            {props.feed.title}
        </span>
    </div>
}

export default withStyles(styles)(withRouter(ImageAndTitle));

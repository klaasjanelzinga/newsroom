import * as React from 'react';
import {withSnackbar, WithSnackbarProps} from 'notistack';
import {RouteComponentProps, withRouter} from 'react-router-dom';
import HeaderBar from '../headerbar/HeaderBar';
import UserProfile from './UserProfile';


interface SignoutProps extends RouteComponentProps, WithSnackbarProps {
}

class SignOut extends React.Component<SignoutProps> {

    componentDidMount() {
        UserProfile.delete();
        this.props.enqueueSnackbar('You were signed out.', {
            variant: 'info',
        });
        this.props.history.push('/');
    }

    render() {
        return <div>
            <HeaderBar />
            Signing out!
        </div>
    }
}

export default withRouter(withSnackbar(SignOut));
  
  
import * as React from 'react'
import {GoogleAuthHandling} from "./GoogleAuthHandling";
import {Subtract} from "utility-types";
import {AuthHandling} from "./index";

export interface WithAuthHandling {
    authHandling: GoogleAuthHandling
}


export const withAuthHandling = <P extends WithAuthHandling>(Component: React.ComponentType<P>) =>
    class MakeCounter extends React.Component<Subtract<P, WithAuthHandling>> {

        render() {
            return <AuthHandling.Consumer>
                {value =>
                    <Component
                        {...this.props as P}
                        authHandling={value}
                    />
                }
            </AuthHandling.Consumer>

        }
    }


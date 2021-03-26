import * as React from "react"
import { Subtract } from "utility-types"
import { AuthHandling } from "./index"
import config from "./Config"
import { UserResponse } from "./user/model"

export interface SignInResult {
    success: boolean
    needs_otp?: boolean
    reason?: string
}

class UserInformation {
    token: string
    email_address: string
    display_name: string | null
    is_approved: boolean
    avatar_image: string | null
    totp_enabled: boolean

    constructor(
        token: string,
        email_address: string,
        display_name: string | null,
        is_approved: boolean,
        avatar_image: string | null,
        totp_enabled: boolean
    ) {
        this.token = token
        this.email_address = email_address
        this.display_name = display_name
        this.is_approved = is_approved
        this.avatar_image = avatar_image
        this.totp_enabled = totp_enabled
    }

    static delete(): void {
        localStorage.removeItem("user-profile")
    }

    static save(user_information: UserInformation): UserInformation {
        localStorage.setItem("user-profile", JSON.stringify(user_information))
        return user_information
    }

    static load(): UserInformation | null {
        const local_storage = localStorage.getItem("user-profile")
        if (local_storage) {
            return JSON.parse(local_storage) as UserInformation
        }
        return null
    }
}

interface ErrorMessage {
    detail: string
}

export interface SignInResponse {
    token: string
    sign_in_state: string
    user: UserResponse
}

interface ChangePasswordResponse {
    success: boolean
    message?: string
}

export class TokenBasedAuthenticator {
    isSignedIn = false
    needs_otp = false
    user_information: UserInformation | null = null

    constructor() {
        this.user_information = UserInformation.load()
        if (this.user_information) {
            this.isSignedIn = true
        }
    }

    /** Return Headers usable for non-authorized calls */
    unsecure_headers(): Headers {
        const headers: HeadersInit = new Headers()
        headers.set("Content-Type", "application/json")
        return headers
    }

    /** Return Headers usable for authorized calls. */
    secure_headers(): Headers {
        const headers: HeadersInit = new Headers()
        headers.set("Content-Type", "application/json")
        headers.set("Authorization", `Bearer ${this.user_information?.token}`)
        return headers
    }

    async sign_in(email_address: string, password: string): Promise<SignInResult> {
        const response = await fetch(`${config.apihost}/user/signin`, {
            headers: this.unsecure_headers(),
            method: "POST",
            body: JSON.stringify({
                email_address: email_address,
                password: password,
            }),
        })

        return await this.parse_response_for_token(response)
    }

    async totp_verification(otp_value: string): Promise<SignInResult> {
        const response = await fetch(`${config.apihost}/user/totp-verification`, {
            headers: this.secure_headers(),
            method: "POST",
            body: JSON.stringify({
                totp_value: otp_value,
            }),
        })

        return await this.parse_response_for_token(response)
    }

    async use_totp_backup_code(backup_code: string): Promise<SignInResult> {
        const response = await fetch(`${config.apihost}/user/use-totp-backup-code`, {
            headers: this.secure_headers(),
            method: "POST",
            body: JSON.stringify({
                totp_backup_code: backup_code,
            }),
        })

        return await this.parse_response_for_token(response)
    }

    async sign_out(): Promise<void> {
        this.isSignedIn = false
        this.user_information = null
        UserInformation.delete()
        return Promise.resolve()
    }

    update_avatar_image(avatar_image: string | null): void {
        if (this.user_information) {
            this.user_information.avatar_image = avatar_image
            UserInformation.save(this.user_information)
        }
    }

    async change_password(
        email_address: string,
        current_password: string,
        new_password: string,
        new_password_repeated: string
    ): Promise<SignInResult> {
        const change_password_response = await fetch(`${config.apihost}/user/change_password`, {
            headers: this.secure_headers(),
            method: "POST",
            body: JSON.stringify({
                email_address: email_address,
                current_password: current_password,
                new_password: new_password,
                new_password_repeated: new_password_repeated,
            }),
        })
        const response = (await change_password_response.json()) as ChangePasswordResponse
        return {
            success: response.success,
            reason: response.message,
        }
    }

    async sign_up(email_address: string, password: string, password_repeated: string): Promise<SignInResult> {
        const response = await fetch(`${config.apihost}/user/signup`, {
            headers: this.unsecure_headers(),
            method: "POST",
            body: JSON.stringify({
                email_address: email_address,
                password: password,
                password_repeated: password_repeated,
            }),
        })

        return await this.parse_response_for_token(response)
    }

    update_user_information(userResponse: UserResponse): void {
        if (this.user_information) {
            this.user_information.display_name = userResponse.display_name
            this.user_information.is_approved = userResponse.is_approved
            UserInformation.save(this.user_information)
        }
    }

    async parse_response_for_token(response: Response): Promise<SignInResult> {
        if (response.status === 200) {
            const json_response = (await response.json()) as SignInResponse
            this.user_information = {
                token: json_response.token,
                email_address: json_response.user.email_address,
                display_name: json_response.user.display_name || "",
                is_approved: json_response.user.is_approved,
                avatar_image: null,
                totp_enabled: json_response.user.totp_enabled,
            }
            UserInformation.save(this.user_information)

            if (json_response.sign_in_state === "REQUIRES_OTP") {
                this.needs_otp = true
                this.isSignedIn = false
            } else {
                this.isSignedIn = true
                this.needs_otp = false
            }
            return Promise.resolve({
                success: true,
                needs_otp: this.needs_otp,
            })
        } else if (response.status === 401) {
            const json_response = (await response.json()) as ErrorMessage
            return Promise.resolve({
                success: false,
                reason: json_response.detail,
            })
        }
        return Promise.resolve({
            success: false,
            reason: "Unknown error",
        })
    }
}

export interface WithAuthHandling {
    authHandling: TokenBasedAuthenticator
}

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
export const withAuthHandling = <P extends WithAuthHandling>(Component: React.ComponentType<P>) =>
    class WithTokenBasedAuthHandler extends React.Component<Subtract<P, WithAuthHandling>> {
        render(): JSX.Element {
            return (
                <AuthHandling.Consumer>
                    {(value): JSX.Element => <Component {...(this.props as P)} authHandling={value} />}
                </AuthHandling.Consumer>
            )
        }
    }

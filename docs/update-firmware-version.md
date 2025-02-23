## Update Firmware Version

* Description: To update the firmware version on devices running an outdated firmware version.

* Prerequisites
    - [Install AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
    - [Configure following profiles](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html):
        - denaribot_dev
        - denaribot_stg
        - denaribot_prod

* Use [update_firmware_version.sh](./scripts/update_firmware_version.sh) to update firmware version
    * **stage**:
        * Description: The stage that you want to deploy to.
        * Allow: dev, stg, prod
        * Default: dev
    * **firmware_version**:
        * Description: The firmware version that you want to update.
        * Allow: string (format x.x.x)
        * Default: 0.0.019
    * **download_url**:
        * Description: The download url of the firmware.
        * Allow: string
        * Default: denaribots-stg-firmware.s3.ap-northeast-1.amazonaws.com

  ```shell
  $ ./scripts/update_firmware_version.sh
    Select a stage:
    - dev
    - stg
    - prod
    Choose from dev, stg, prod [dev]: dev
    Enter firmware_version [0.0.019]: 0.0.019
    Enter download_url [denaribots-stg-firmware.s3.ap-northeast-1.amazonaws.com]: denaribots-stg-firmware.s3.ap-northeast-1.amazonaws.com

    Summary:
    STAGE - dev
    FIRMWARE VERSION - 0.0.019
    DOWNLOAD URL - denaribots-stg-firmware.s3.ap-northeast-1.amazonaws.com

    Continue to update firmware? (y/n) [y]:
    Starting firmware update for '0.0.019' on dev
    Check firmware update triggered at 2025-02-13 15:00:00
    Check firmware update triggered at 2025-02-13 15:15:00
    Check firmware update triggered at 2025-02-13 15:30:00
    Check firmware update triggered at 2025-02-13 15:45:00
    Check firmware update triggered at 2025-02-13 16:00:00
  ```

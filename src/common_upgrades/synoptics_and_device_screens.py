from functools import partial


class SynopticsAndDeviceScreens(object):
    """Manipulate an instrument's synoptics and device_screens
    """

    def __init__(self, file_access, logger):
        self.file_access = file_access
        self.logger = logger
        self._update_keys_in_device_screens = partial(
            self._update_opi_keys_in_xml, root_tag="device", key_tag="key"
        )
        self._update_keys_in_synoptics = partial(
            self._update_opi_keys_in_xml, root_tag="target", key_tag="name"
        )

    def update_opi_keys(self, keys_to_update):
        """Update the OPI keys in all synoptics and device screens

        Args:
            keys_to_update (Dict)): The OPI keys that need updating as a dictionary with {old_key: new_key}

        Returns:
            exit code 0 success; anything else fail

        """
        result = 0
        try:
            synoptics = self.file_access.get_synoptic_files()
            device_screens = self.file_access.get_device_screens()
        except OSError:
            result = -1
        else:
            for path, xml in synoptics:
                try:
                    self._update_keys_in_synoptics(path, xml, keys_to_update)
                except Exception as e:
                    self.logger.error("Cannot upgrade synoptic {}: {}".format(path, e))
                    result = -2
                    break
            try:
                if device_screens:
                    self._update_keys_in_device_screens(
                        device_screens[0], device_screens[1], keys_to_update
                    )
            except Exception as e:
                self.logger.error("Cannot upgrade device screens {}: {}".format(path, e))
                result = -2
        return result

    def _update_opi_keys_in_xml(self, path, xml, keys_to_update, root_tag, key_tag):
        """Replaces an opi key with a different key

        Args:
            path (String): path to file to update
            xml (String): xml of the file to update
            keys_to_update (Dict): A dictionary with {old_key: new_key}
            root_tag (String): The root tag to find the opi in
            key_tag (String): The tag to find teh key in
        """
        file_changed = False
        for target_element in xml.getElementsByTagName(root_tag):
            key_element = target_element.getElementsByTagName(key_tag)[0]
            old_key = key_element.firstChild.nodeValue
            new_key = keys_to_update.get(old_key, old_key)
            key_element.firstChild.nodeValue = new_key
            if new_key != old_key:
                file_changed = True
                self.logger.info(
                    "OPI key '{}' replaced with corresponding key '{}' in {}".format(
                        old_key, new_key, path
                    )
                )
        if file_changed:
            self.file_access.write_xml_file(path, xml)

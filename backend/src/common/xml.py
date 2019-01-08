class Xml:
  @staticmethod
  # Gets the property named {@code name} within the xml element.
  # expected_values: Set. If present, an exception will be raised if the named property does not have a value
  #     within the expected_values set.
  def get_property(xml_element, name, expected_values=None):
    value = xml_element.get(name)
    if expected_values and value not in expected_values:
      raise Exception("Unexpected property")
    return value

  # Verifies the xml_element tag is within the {@code expected_tags} set.
  @staticmethod
  def verify_tag(xml_element, expected_tags):
    if xml_element.tag not in expected_tags:
      raise Exception("Expected tag not found.")
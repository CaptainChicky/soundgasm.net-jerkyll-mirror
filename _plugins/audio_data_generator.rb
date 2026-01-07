# Require ActiveSupport extensions for the String class
require 'active_support/core_ext/string'

# Define a custom generator for Jekyll
module Jekyll
  # AudioDataGenerator is responsible for generating new audio entry pages
  class AudioDataGenerator < Generator
    safe true
    
    # The generate method is called during Jekyll's build process
    def generate(site)
      # Load the 'audio_data' from the _data/audio_data.yml file
      audio_data = site.data['audio_data']['users']
      
      # Iterate over each user in the audio data
      audio_data.each do |user, entries|
        # Iterate over each audio entry for this user
        entries.each do |entry|
          # For each audio entry, create a new AudioEntryPage
          site.pages << AudioEntryPage.new(site, site.source, user, entry)
        end
      end
    end
  end
  
  # Define a class for representing an individual audio entry page
  class AudioEntryPage < Page
    # Initialize the AudioEntryPage with the site, base, user, and entry data
    def initialize(site, base, user, entry)
      @site = site 
      @base = base 
      
      # Set the directory path for this audio entry page, e.g., /u/username
      @dir = File.join('u', user)
      
      # Sanitize the title more aggressively to handle Unicode emoticons
      sanitized_title = sanitize_title(entry['title'])
      @name = "#{sanitized_title}.html"
      
      # Process the page (set up the page with the correct name)
      self.process(@name)
      
      # Read the layout template for this page from _layouts/entry.html
      self.read_yaml(File.join(base, '_layouts'), 'entry.html')
      
      # Set page-specific data, which can be used in the layout to render the page
      self.data['title'] = entry['title']      # Keep original title for display
      self.data['description'] = entry['description']
      self.data['audio'] = entry['audio']
      self.data['user'] = user
      self.data['sanitized_title'] = sanitized_title  # Store sanitized version for linking
    end
    
    private
    
    # Custom sanitization method that handles Unicode better than parameterize
    def sanitize_title(title)
      # First, remove all Unicode emoticons and special characters
      # Keep only ASCII letters, numbers, spaces, and basic punctuation
      cleaned = title.gsub(/[^\x00-\x7F]+/, '') # Remove all non-ASCII characters
      
      # Now use parameterize on the cleaned string
      cleaned.parameterize
    end
  end
end